"""Oracle Agent — Autonomous Marketplace Signup via Playwright.

Uses Playwright to navigate settings pages, generate API keys,
and store them in Agent Vault. Fully autonomous, zero human interaction.

Usage: python3 oracle/marketplace_signup.py
"""
import asyncio
import subprocess
import json
import re
import os
from pathlib import Path

VAULT = "oracle"


async def save_to_vault(key: str, value: str) -> bool:
    """Store credential in Agent Vault."""
    result = subprocess.run(
        ['agent-vault', 'vault', 'credential', 'set', f'{key}={value}', '--vault', VAULT],
        capture_output=True, text=True, timeout=10
    )
    return result.returncode == 0


async def generate_modrinth_token(page):
    """Navigate to Modrinth settings and generate PAT."""
    print("  Navigating to Modrinth settings...")
    await page.goto("https://modrinth.com/settings/account")
    await page.wait_for_load_state("networkidle")
    
    # Look for PAT generation
    # Modrinth has a "Create new token" button
    try:
        btn = page.locator("text=Create new token").first
        if await btn.is_visible(timeout=5000):
            await btn.click()
            await page.wait_for_timeout(2000)
            
            # Fill token name
            name_input = page.locator("input[placeholder*='name'], input[name*='name']").first
            if await name_input.is_visible(timeout=3000):
                await name_input.fill("oracle-agent")
                await page.wait_for_timeout(500)
            
            # Click create/submit
            create_btn = page.locator("button:has-text('Create'), button:has-text('Generate'), button[type='submit']").first
            if await create_btn.is_visible(timeout=3000):
                await create_btn.click()
                await page.wait_for_timeout(3000)
                
                # Try to find the token in the page
                content = await page.content()
                token_match = re.search(r'mrp_[A-Za-z0-9_-]{20,}', content)
                if token_match:
                    token = token_match.group(0)
                    await save_to_vault("MODRINTH_PAT", token)
                    print(f"  ✓ Modrinth PAT saved: {token[:20]}...")
                    return True
    except Exception as e:
        print(f"  ✗ Modrinth failed: {e}")
    return False


async def generate_itchio_token(page):
    """Navigate to itch.io settings and generate API key."""
    print("  Navigating to itch.io API keys...")
    await page.goto("https://itch.io/settings/api-keys")
    await page.wait_for_load_state("networkidle")
    
    try:
        # itch.io has a "Generate API key" button
        btn = page.locator("text=Generate").first
        if await btn.is_visible(timeout=5000):
            await btn.click()
            await page.wait_for_timeout(3000)
            
            # Find the generated key
            content = await page.content()
            # itch.io keys are typically long alphanumeric strings
            key_match = re.search(r'api[_-]?key["\s:=]+([a-zA-Z0-9]{30,})', content, re.IGNORECASE)
            if key_match:
                key = key_match.group(1)
                await save_to_vault("ITCH_API_KEY", key)
                print(f"  ✓ itch.io API key saved: {key[:20]}...")
                return True
    except Exception as e:
        print(f"  ✗ itch.io failed: {e}")
    return False


async def generate_gumroad_token(page):
    """Navigate to Gumroad settings and generate access token."""
    print("  Navigating to Gumroad advanced settings...")
    await page.goto("https://gumroad.com/settings/advanced")
    await page.wait_for_load_state("networkidle")
    
    try:
        # Gumroad has a "Generate access token" button
        btn = page.locator("text=Generate").first
        if await btn.is_visible(timeout=5000):
            await btn.click()
            await page.wait_for_timeout(3000)
            
            content = await page.content()
            # Gumroad tokens are typically long strings
            token_match = re.search(r'token["\s:=]+([a-zA-Z0-9_-]{20,})', content, re.IGNORECASE)
            if token_match:
                token = token_match.group(1)
                await save_to_vault("GUMROAD_ACCESS_TOKEN", token)
                print(f"  ✓ Gumroad token saved: {token[:20]}...")
                return True
    except Exception as e:
        print(f"  ✗ Gumroad failed: {e}")
    return False


async def generate_monday_token(page):
    """Navigate to monday.com and generate API token."""
    print("  Navigating to monday.com API...")
    await page.goto("https://developer.monday.com/apps#/my-access-tokens")
    await page.wait_for_load_state("networkidle")
    
    try:
        btn = page.locator("text=Generate").first
        if await btn.is_visible(timeout=5000):
            await btn.click()
            await page.wait_for_timeout(3000)
            
            content = await page.content()
            token_match = re.search(r'eyJ[A-Za-z0-9_-]{20,}', content)
            if token_match:
                token = token_match.group(0)
                await save_to_vault("MONDAY_API_TOKEN", token)
                print(f"  ✓ monday.com token saved: {token[:20]}...")
                return True
    except Exception as e:
        print(f"  ✗ monday.com failed: {e}")
    return False


async def generate_linear_token(page):
    """Navigate to Linear and generate API key."""
    print("  Navigating to Linear API settings...")
    await page.goto("https://linear.app/settings/api")
    await page.wait_for_load_state("networkidle")
    
    try:
        btn = page.locator("text=Create").first
        if await btn.is_visible(timeout=5000):
            await btn.click()
            await page.wait_for_timeout(2000)
            
            # Fill name
            name_input = page.locator("input").first
            if await name_input.is_visible(timeout=3000):
                await name_input.fill("oracle-agent")
                await page.wait_for_timeout(500)
            
            create_btn = page.locator("button:has-text('Create'), button[type='submit']").first
            if await create_btn.is_visible(timeout=3000):
                await create_btn.click()
                await page.wait_for_timeout(3000)
                
                content = await page.content()
                # Linear keys start with lin_api_
                key_match = re.search(r'lin_api_[A-Za-z0-9_-]{20,}', content)
                if key_match:
                    key = key_match.group(0)
                    await save_to_vault("LINEAR_API_KEY", key)
                    print(f"  ✓ Linear API key saved: {key[:20]}...")
                    return True
    except Exception as e:
        print(f"  ✗ Linear failed: {e}")
    return False


async def generate_notion_token(page):
    """Navigate to Notion integrations and create one."""
    print("  Navigating to Notion integrations...")
    await page.goto("https://www.notion.so/my-integrations")
    await page.wait_for_load_state("networkidle")
    
    try:
        btn = page.locator("text=New integration").first
        if await btn.is_visible(timeout=5000):
            await btn.click()
            await page.wait_for_timeout(2000)
            
            # Fill name
            name_input = page.locator("input[name='name'], input[placeholder*='name']").first
            if await name_input.is_visible(timeout=3000):
                await name_input.fill("oracle-agent")
                await page.wait_for_timeout(500)
            
            # Select workspace
            # Submit
            submit_btn = page.locator("button:has-text('Submit'), button:has-text('Create'), button[type='submit']").first
            if await submit_btn.is_visible(timeout=3000):
                await submit_btn.click()
                await page.wait_for_timeout(3000)
                
                content = await page.content()
                # Notion tokens start with secret_ or ntn_
                token_match = re.search(r'(secret_[A-Za-z0-9_-]{20,}|ntn_[A-Za-z0-9_-]{20,})', content)
                if token_match:
                    token = token_match.group(0)
                    await save_to_vault("NOTION_TOKEN", token)
                    print(f"  ✓ Notion token saved: {token[:20]}...")
                    return True
    except Exception as e:
        print(f"  ✗ Notion failed: {e}")
    return False


async def generate_huggingface_token(page):
    """Navigate to HuggingFace and generate token."""
    print("  Navigating to HuggingFace tokens...")
    await page.goto("https://huggingface.co/settings/tokens")
    await page.wait_for_load_state("networkidle")
    
    try:
        btn = page.locator("text=Create new token").first
        if await btn.is_visible(timeout=5000):
            await btn.click()
            await page.wait_for_timeout(2000)
            
            # Fill name
            name_input = page.locator("input[name='name'], input[placeholder*='name']").first
            if await name_input.is_visible(timeout=3000):
                await name_input.fill("oracle-agent")
                await page.wait_for_timeout(500)
            
            # Select role
            role_select = page.locator("select[name='role'], [role='combobox']").first
            if await role_select.is_visible(timeout=2000):
                await role_select.select_option("read")
            
            create_btn = page.locator("button:has-text('Create'), button[type='submit']").first
            if await create_btn.is_visible(timeout=3000):
                await create_btn.click()
                await page.wait_for_timeout(3000)
                
                content = await page.content()
                # HF tokens start with hf_
                token_match = re.search(r'hf_[A-Za-z0-9_-]{20,}', content)
                if token_match:
                    token = token_match.group(0)
                    await save_to_vault("HUGGINGFACE_TOKEN", token)
                    print(f"  ✓ HuggingFace token saved: {token[:20]}...")
                    return True
    except Exception as e:
        print(f"  ✗ HuggingFace failed: {e}")
    return False


async def generate_replicate_token(page):
    """Navigate to Replicate and generate token."""
    print("  Navigating to Replicate API tokens...")
    await page.goto("https://replicate.com/account/api-tokens")
    await page.wait_for_load_state("networkidle")
    
    try:
        btn = page.locator("text=Create token").first
        if await btn.is_visible(timeout=5000):
            await btn.click()
            await page.wait_for_timeout(2000)
            
            # Fill name
            name_input = page.locator("input").first
            if await name_input.is_visible(timeout=3000):
                await name_input.fill("oracle-agent")
                await page.wait_for_timeout(500)
            
            create_btn = page.locator("button:has-text('Create'), button[type='submit']").first
            if await create_btn.is_visible(timeout=3000):
                await create_btn.click()
                await page.wait_for_timeout(3000)
                
                content = await page.content()
                # Replicate tokens start with r8_
                token_match = re.search(r'r8_[A-Za-z0-9_-]{20,}', content)
                if token_match:
                    token = token_match.group(0)
                    await save_to_vault("REPLICATE_TOKEN", token)
                    print(f"  ✓ Replicate token saved: {token[:20]}...")
                    return True
    except Exception as e:
        print(f"  ✗ Replicate failed: {e}")
    return False


# Marketplaces that can be done via API (no browser needed)
API_SIGNUPS = {
    "AgentPact": {
        "url": "https://api.agentpact.xyz/api/auth/register",
        "method": "POST",
        "body": lambda: {"agentId": __import__('uuid').uuid4().hex},
        "extract": lambda r: r.get("apiKey"),
        "vault_key": "AGENTPACT_API_KEY",
    },
}


async def api_signup(name: str, config: dict):
    """Signup via API (no browser needed)."""
    import urllib.request
    import uuid
    
    print(f"  API signup: {name}...")
    try:
        body = json.dumps(config["body"]()).encode()
        req = urllib.request.Request(
            config["url"],
            data=body,
            headers={"Content-Type": "application/json"},
            method=config.get("method", "POST")
        )
        resp = urllib.request.urlopen(req, timeout=10)
        data = json.loads(resp.read())
        token = config["extract"](data)
        if token:
            await save_to_vault(config["vault_key"], token)
            print(f"  ✓ {name} saved: {token[:20]}...")
            return True
    except Exception as e:
        print(f"  ✗ {name} failed: {e}")
    return False


async def main():
    from playwright.async_api import async_playwright
    
    print("=" * 60)
    print("ORACLE AGENT — AUTONOMOUS MARKETPLACE SIGNUP")
    print("=" * 60)
    
    # Phase 1: API signups (no browser needed)
    print("\n--- Phase 1: API Signups ---")
    for name, config in API_SIGNUPS.items():
        await api_signup(name, config)
    
    # Phase 2: Browser-based signups
    print("\n--- Phase 2: Browser Signups ---")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, executable_path='/root/.agent-browser/browsers/chrome-152.0.7977.54/chrome')
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        # Try each marketplace
        marketplaces = [
            ("Modrinth", generate_modrinth_token),
            ("itch.io", generate_itchio_token),
            ("Gumroad", generate_gumroad_token),
            ("monday.com", generate_monday_token),
            ("Linear", generate_linear_token),
            ("Notion", generate_notion_token),
            ("HuggingFace", generate_huggingface_token),
            ("Replicate", generate_replicate_token),
        ]
        
        results = {}
        for name, func in marketplaces:
            print(f"\n[{name}]")
            try:
                result = await func(page)
                results[name] = result
            except Exception as e:
                print(f"  ✗ {name} error: {e}")
                results[name] = False
        
        await browser.close()
    
    # Summary
    print("\n" + "=" * 60)
    print("RESULTS")
    print("=" * 60)
    for name, success in results.items():
        status = "✓" if success else "✗"
        print(f"  {status} {name}")
    
    # Check vault
    print("\n--- Vault Status ---")
    result = subprocess.run(
        ['agent-vault', 'vault', 'credential', 'list', '--vault', VAULT],
        capture_output=True, text=True, timeout=10
    )
    print(result.stdout)


if __name__ == "__main__":
    asyncio.run(main())
