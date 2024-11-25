import asyncio
import aiohttp

async def fetch_article(session, url):
    headers = {
        'Content-Type': 'application/json',
    }
    json_data = {
        'articleUrl': url,
        'regenerate': 'true',
    }

    try:
        async with session.post(
            'https://d5dvsartlv83ra2p2eek.apigw.yandexcloud.net/summarize-pdf',
            headers=headers,
            json=json_data,
            timeout=360  # Set to 6 minutes
        ) as response:
            if response.status == 200:
                result = await response.text()
                print(f"Success: {url}")
                return result
            else:
                print(f"Failed with status: {response.status} for {url}")
    except asyncio.TimeoutError:
        print(f"Timeout occurred for {url}")
    except Exception as e:
        print(f"An error occurred: {e} for {url}")

async def main():
    urls = [
        # 'https://onlinelibrary.wiley.com/doi/full/10.1111/pde.15781',
        # 'https://onlinelibrary.wiley.com/doi/full/10.1111/pde.15782',
        # 'https://onlinelibrary.wiley.com/doi/10.1111/pde.15792',
        # 'https://onlinelibrary.wiley.com/doi/10.1111/pde.15790',
        # 'https://onlinelibrary.wiley.com/doi/10.1111/pde.15807',
        # 'https://onlinelibrary.wiley.com/doi/10.1111/pde.15817',
        # 'https://onlinelibrary.wiley.com/doi/10.1111/pde.15813',
        # 'https://onlinelibrary.wiley.com/doi/10.1111/pde.15768',
        # 'https://onlinelibrary.wiley.com/doi/10.1111/pde.15799',


        # 'https://onlinelibrary.wiley.com/doi/10.1111/pde.15819',
        # 'https://onlinelibrary.wiley.com/doi/10.1111/pde.15805',
        # 'https://onlinelibrary.wiley.com/doi/full/10.1111/pde.15805',
        # "https://onlinelibrary.wiley.com/doi/10.1111/pde.15710",
        # 'https://www.pubmed.ncbi.nlm.nih.gov/38931395/',
        # 'https://www.pubmed.ncbi.nlm.nih.gov/38921259/',
        # 'https://www.pubmed.ncbi.nlm.nih.gov/38915336/', # for fix title
        # 'https://onlinelibrary.wiley.com/doi/10.1111/pde.15578',
        # 'https://onlinelibrary.wiley.com/doi/10.1111/pde.15472',
        # 'https://onlinelibrary.wiley.com/doi/10.1111/pde.15394',
        # 'https://onlinelibrary.wiley.com/doi/10.1111/pde.15114',
        # 'https://onlinelibrary.wiley.com/doi/10.1111/pde.15026',
        # 'https://onlinelibrary.wiley.com/doi/10.1111/pde.15223',
        # 'https://onlinelibrary.wiley.com/doi/10.1111/pde.15720',
        # 'https://onlinelibrary.wiley.com/doi/10.1111/pde.15372',
        # 'https://onlinelibrary.wiley.com/doi/10.1111/pde.15266',
        # 'https://onlinelibrary.wiley.com/doi/10.1111/pde.15379',
        # 'https://onlinelibrary.wiley.com/doi/10.1111/pde.15010',
        

        # Add more URLs here
    ]

    async with aiohttp.ClientSession() as session:
        tasks = [fetch_article(session, url) for url in urls]
        await asyncio.gather(*tasks)

# Run the async function
asyncio.run(main())