import asyncio
from playwright.async_api import async_playwright
from dotenv import load_dotenv
import os
import json
from datetime import datetime
import time

load_dotenv()

TITAN_API_USERNAME = os.getenv("TITAN_API_USERNAME")
TITAN_API_PASSWORD = os.getenv("TITAN_API_PASSWORD")

TITAN_API_BASE_URL = "https://developer.titandms.com.au"

def generate_markdown(apis):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    markdown = f"# Titan DMS API Documentation\n\nGenerated on: {timestamp}\n\n"
    
    for api in apis:
        markdown += f"## {api['name']}\n\n"
        markdown += f"**Type:** {api['type']}\n\n"
        markdown += f"**Description:** {api['description']}\n\n"
        markdown += f"**URL:** {api['url']}\n\n"
        
        if api['details']:
            markdown += "### Operations\n\n"
            for operation in api['details'].get('operations', []):
                markdown += f"#### {operation['method']} {operation['name']}\n\n"
                if operation.get('description'):
                    markdown += f"{operation['description']}\n\n"
                if operation.get('endpoint'):
                    markdown += f"**Endpoint:** `{operation['endpoint']}`\n\n"
                if operation.get('request'):
                    markdown += "**Request:**\n```json\n"
                    markdown += json.dumps(operation['request'], indent=2)
                    markdown += "\n```\n\n"
                if operation.get('response'):
                    markdown += "**Response:**\n```json\n"
                    markdown += json.dumps(operation['response'], indent=2)
                    markdown += "\n```\n\n"
        
        markdown += "---\n\n"
    
    return markdown

async def wait_for_network_idle(page, timeout=30000):
    """Wait for network to be idle and no more than 0 connections for at least 500ms"""
    try:
        await page.wait_for_load_state('networkidle', timeout=timeout)
        # Additional wait to ensure everything is stable
        await page.wait_for_timeout(2000)
    except Exception as e:
        print(f"Warning: Network idle wait timed out: {e}")

async def scrape_api_details(page, api_url):
    try:
        print(f"\nNavigating to API: {api_url}")
        await page.goto(api_url, wait_until='networkidle')
        
        # Wait for the API details to load
        print("Waiting for API details to load...")
        await page.wait_for_selector('api-details', timeout=10000)
        await wait_for_network_idle(page)
        
        details = {}
        
        # Get API title
        title_el = await page.query_selector('h1.flex.align-items-center span')
        details['title'] = await title_el.inner_text() if title_el else ""
        print(f"Found API: {details['title']}")
        
        # Get API description
        description_el = await page.query_selector('api-details p')
        details['description'] = await description_el.inner_text() if description_el else ""
        
        # Get operations
        operations = []
        
        # Wait for the operation list to load
        print("Waiting for operations list to load...")
        await page.wait_for_selector('operation-list', timeout=10000)
        await page.wait_for_selector('operation-list .list-item', timeout=10000)
        await wait_for_network_idle(page)
        
        # Get all operation elements
        operation_elements = await page.query_selector_all('operation-list .list-item')
        print(f"Found {len(operation_elements)} operations")
        
        for i, op_el in enumerate(operation_elements):
            try:
                print(f"\nProcessing operation {i+1}/{len(operation_elements)}")
                
                # Re-get the operation elements to avoid stale references
                operation_elements = await page.query_selector_all('operation-list .list-item')
                op_el = operation_elements[i]
                
                # Get method
                method_el = await op_el.query_selector('.http-method')
                method = await method_el.evaluate('el => el.getAttribute("data-method")')
                
                # Get operation name
                name_el = await op_el.query_selector('.text-truncate')
                name = await name_el.inner_text() if name_el else ""
                
                print(f"Processing: {method} {name}")
                
                # Click the operation to get details
                await op_el.click()
                await page.wait_for_selector('operation-details', timeout=10000)
                await wait_for_network_idle(page)
                
                # Wait a bit for the details to load
                await page.wait_for_timeout(2000)
                
                # Get operation description
                desc_el = await page.query_selector('operation-details p')
                description = await desc_el.inner_text() if desc_el else ""
                
                # Get request URL
                url_el = await page.query_selector('operation-details .text-monospace')
                url = await url_el.inner_text() if url_el else ""
                
                # Get response example
                response_el = await page.query_selector('operation-details pre')
                response_text = await response_el.inner_text() if response_el else ""
                
                # Try to parse response as JSON if it's valid JSON
                try:
                    response = json.loads(response_text)
                except:
                    response = response_text
                
                operations.append({
                    'method': method,
                    'name': name,
                    'description': description,
                    'endpoint': url,
                    'response': response
                })
                
                print(f"Completed: {method} {name}")
                
                # Click the operation again to collapse it
                await op_el.click()
                await page.wait_for_timeout(1000)
                
            except Exception as e:
                print(f"Error processing operation: {e}")
                continue
        
        details['operations'] = operations
        print(f"\nCompleted processing API: {details['title']}")
        return details
    except Exception as e:
        print(f"Error scraping API details from {api_url}: {e}")
        return None

async def get_api_list(page):
    try:
        print("\nGetting API list...")
        # Go to the APIs page
        await page.goto(f"{TITAN_API_BASE_URL}/apis", wait_until='networkidle')
        await page.wait_for_selector('div.table-body .table-row', timeout=10000)
        await wait_for_network_idle(page)
        
        # Extract API information
        api_rows = await page.query_selector_all('div.table-body .table-row')
        apis = []
        
        for row in api_rows:
            try:
                name_el = await row.query_selector('div.col-5.text-truncate a')
                if not name_el:
                    continue
                    
                name = await name_el.inner_text()
                api_link = await name_el.get_attribute('href')
                
                description_el = await row.query_selector('div.col-5 p')
                description = await description_el.inner_text() if description_el else ""
                
                api_type_el = await row.query_selector('div.col-2')
                api_type = await api_type_el.inner_text() if api_type_el else ""
                
                apis.append({
                    'name': name.strip(),
                    'description': description.strip(),
                    'type': api_type.strip(),
                    'url': f"{TITAN_API_BASE_URL}{api_link}",
                    'link': api_link
                })
                
            except Exception as e:
                print(f"Error extracting API info from row: {e}")
                continue
                
        return apis
    except Exception as e:
        print(f"Error getting API list: {e}")
        return []

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = await context.new_page()

        try:
            print("Starting API documentation scraper...")
            
            # Go to the developer portal
            await page.goto(TITAN_API_BASE_URL, wait_until='networkidle')
            await wait_for_network_idle(page)

            # Click the "Sign in" button
            await page.wait_for_selector('a.nav-link[href^="/signin"]', timeout=10000)
            await page.click('a.nav-link[href^="/signin"]')

            # Wait for navigation to the login form
            await page.wait_for_selector("input#Email", timeout=10000)
            await wait_for_network_idle(page)

            # Enter credentials
            await page.fill('input#Email', TITAN_API_USERNAME)
            await page.fill('input#Password', TITAN_API_PASSWORD)

            # Click sign-in button
            await page.click('button[type="submit"].btn-primary')

            # Wait for navigation to complete after login
            await page.wait_for_selector('a.button-primary[href="/apis"]', timeout=10000)
            await wait_for_network_idle(page)

            # Get the list of APIs first
            apis = await get_api_list(page)
            print(f"Found {len(apis)} APIs to process")
            
            # Process each API
            for i, api in enumerate(apis):
                try:
                    print(f"\nProcessing API {i+1}/{len(apis)}: {api['name']}")
                    api_details = await scrape_api_details(page, api['url'])
                    
                    if api_details:
                        api['details'] = api_details
                        print(f"Successfully processed {api['name']}")
                    else:
                        print(f"Failed to get details for {api['name']}")
                    
                    # Wait a bit before processing the next API
                    await page.wait_for_timeout(3000)
                        
                except Exception as e:
                    print(f"Error processing API {api['name']}: {e}")
                    continue

            # Save the results
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Save as JSON
            with open(f'api_docs_{timestamp}.json', 'w', encoding='utf-8') as f:
                json.dump(apis, f, indent=2, ensure_ascii=False)
            
            # Save as Markdown
            markdown_content = generate_markdown(apis)
            with open(f'api_docs_{timestamp}.md', 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            print(f"\nDocumentation has been saved to:")
            print(f"- api_docs_{timestamp}.json")
            print(f"- api_docs_{timestamp}.md")

        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            await browser.close()

# Run the scraper
if __name__ == "__main__":
    asyncio.run(main())
