"""LabContext — Hydra-backed broker, progressive disclosure."""
from __future__ import annotations
import json, time
try:
    from hydra.store import HydraStore
except ImportError:
    from workerkit.hydra.store import HydraStore

class LabContext:
    def __init__(self, hydra: HydraStore, worker_id: str):
        self.hydra=hydra; self.worker_id=worker_id
    def recall_similar_runs(self, task_family: str, limit=5)->list[dict]:
        runs=self.hydra.get_runs(limit=200)
        filt=[r for r in runs if task_family.lower() in (r.get("skills","")+r.get("opportunity_id","")+r.get("model","")).lower() or task_family.lower() in json.dumps(r).lower()]
        wins=[r for r in filt if r.get("outcome")=="won"][:limit]
        return [{"run_id":r["run_id"],"score":r.get("evaluation_score"),"model":r.get("model"),"skills":json.loads(r["skills"]) if isinstance(r["skills"],str) else r["skills"]} for r in (wins or filt[:limit])]
    def get_task_priors(self, task_family: str)->dict:
        runs=self.hydra.get_runs(limit=500); fam=[r for r in runs if task_family.lower() in json.dumps(r).lower()]
        if not fam: fam=runs
        won=sum(1 for r in fam if r.get("outcome")=="won"); tot=sum(1 for r in fam if r.get("outcome") in ("won","lost"))
        return {"task_family":task_family,"n":len(fam),"win_rate":round(won/max(1,tot),2),"avg_score":round(sum(r.get("evaluation_score",0) for r in fam)/max(1,len(fam)),3)}
    def get_failure_patterns(self, role: str)->list[dict]:
        rows=self.hydra.get_runs(limit=200); losses=[r for r in rows if r.get("outcome")=="lost"]
        # derive from low scores; no failure_reason column -> use evaluation_score bucket
        buckets={}
        for r in losses: k=f"low_score_{int(r.get('evaluation_score',0)*10)}"; buckets[k]=buckets.get(k,0)+1
        return sorted([{"pattern":k,"count":v} for k,v in buckets.items()],key=lambda x:-x["count"])[:3]
    def get_best_skill(self, task_family: str)->dict|None:
        cor=self.hydra.skill_win_correlation()
        if cor:
            cand=[c for c in cor if task_family.lower() in c["skill"].lower()]
            best=(cand[0] if cand else cor[0])
            return {"skill":best["skill"],"win_rate":best["win_rate"],"n":best["n"]}
        return None
    def record_observation(self, run_id: str, data: dict)->None:
        # projections are derived; store as insight if evidence present
        if data.get("failure_reason"): self.hydra.add_insight(f"obs_{run_id}", data["failure_reason"][:80], json.dumps(data)[:400], 1, 0.5)
    def brief(self, task_family: str)->str:
        pri=self.get_task_priors(task_family); sim=self.recall_similar_runs(task_family,3)
        skill=self.get_best_skill(task_family); fails=self.get_failure_patterns(task_family)
        econ=self.hydra.profitability_by_model()
        econ_line=", ".join(f"{e['model']}:${e['avg_profit']:.2f}" for e in econ[:2]) if econ else "n/a"
        lines=[f"# LAB BRIEF — {task_family}",f"**Worker** {self.worker_id}","",f"Task family: {task_family}",f"Prior runs: {pri['n']}  win_rate: {pri['win_rate']:.0%}  avg_score: {pri['avg_score']}",f"Best skill: {skill['skill']} ({skill['win_rate']:.0%} n={skill['n']})" if skill else "Best skill: n/a",f"Model economics: {econ_line}",""]
        if sim: lines+=["Similar wins:"]+[f"- {s['run_id']} score={s['score']} model={s['model']}" for s in sim]
        if fails: lines+=["","Failure warnings:"]+[f"- {f['pattern']} x{f['count']}" for f in fails]
        lines+=["","*Full trajectories on demand — ask for run_id.*"]
        return "\n".join(lines)
