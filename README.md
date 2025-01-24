# Issuu Downloader
This is a GUI application created in Python to download publications from [Issuu](https://issuu.com/) website, even if the download has been disbabled by the uploader. This was initially created to archive the "*[Mihaaru](https://issuu.com/mihaaru/)*" publications on Issuu. 

Using this you will be able to download publications either page by page as images, or as a compiled PDF (or even both).

## Libraries Used:
- `PyQt5`
- `fpdf`
- `pillow`
- `BeautifulSoup4`
- `httpx[http2]`

## Screenshots:
![](/ss.png?raw=true)

## How to use:
1) Paste the respective link to the publication
2) Select a location to save it
3) If you want to save as image, check the image box, or if you would like as a PDF check the PDF. (If you want both, then keep them both checked.)
4) Click "Go!" and the download will begin.