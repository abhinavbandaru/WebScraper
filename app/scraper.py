import httpx
from bs4 import BeautifulSoup
import asyncio
import aiofiles
from pathlib import Path

class Scraper:
    def __init__(self, url="https://dentalstall.com/shop/",
                 pages=1, proxy: str = None) -> None:
        self.url = url
        self.pages = pages
        self.proxy = proxy
        self.proxies = {"http": proxy, "https": proxy} if proxy else None
        self.headers = {"User-Agent": "Mozilla/5.0"}
        self.session = httpx.AsyncClient(proxies=self.proxy)\
                        if proxy else httpx.AsyncClient()


    async def getPage(self, url: str):
        retries = 3
        for _ in range(retries):
            try:
                response = await self.session.get(url, headers=self.headers)
                if response.status_code == 200:
                    return response
            except httpx.RequestError as exc:
                print(f"Error fetching {url}: {exc}")
            finally:
                await asyncio.sleep(2)

        return None

    
    async def getTitle(self, url: str) -> str:
        response = await self.getPage(url)
        if not response:
            return None

        soup = BeautifulSoup(response.content, 'html.parser')
        title = soup.find('h1', class_='product_title')

        return title.get_text(strip=True) if title else None


    async def downloadImg(self, url: str, title: str):
        imageDir = Path("static/images")
        imageDir.mkdir(parents=True, exist_ok=True)

        imagePath = imageDir / f"{title.replace(' ', '_')}.jpg"
        try:
            response = await self.session.get(url)
            async with aiofiles.open(imagePath, "wb") as f:
                await f.write(response.content)
            return str(imagePath)
        except Exception as e:
            print(f"Failed to download image: {e}")
            return None

    
    async def getImgPath(self, title, item):
        if not item:
            return None

        imageTag = item.find('img', attrs={'class': 'attachment-woocommerce_thumbnail'})
        imagePath = None
    
        if imageTag:
            imageUrl = imageTag.get('data-lazy-src')
            if imageUrl and not imageUrl.startswith("data:image"):
                imagePath = await self.downloadImg(imageUrl, title)
            else:
                print(f"No valid image URL found for {title}")
        else:
            print(f"Image tag not found for {title}")

        return imagePath if imagePath else ""


    async def getItemsFromPage(self, response) -> list[dict]:
        soup = BeautifulSoup(response.content, 'html.parser')
        productItems = soup.find_all('div', class_='product-inner')
        products = []
        for item in productItems:
            itemUrl = item.find('h2', class_='woo-loop-product__title').find('a')['href']
            title = await self.getTitle(itemUrl)
            if not title:
                title = item.find('h2', class_='woo-loop-product__title').get_text(strip=True)

            price = item.find('span', class_='woocommerce-Price-amount')\
                .get_text(strip=True).replace("\u20b9", "").replace(",", "")
            price = float(price)

            imagePath = await self.getImgPath(title, item)

            products.append({
                "title": title,
                "price": price,
                "image": imagePath,
            })

        return products


    async def scrapePage(self, pageNo: int):
        url = self.url
        if pageNo != 1:
            url += f"page/{pageNo}/"
        pageResponse = await self.getPage(url)
        
        return await self.getItemsFromPage(pageResponse)
    

    async def scrape(self):
        products = []
        for pageNo in range(1, self.pages + 1):
            pageProducts = await self.scrapePage(pageNo)
            products.extend(pageProducts)
        
        return products