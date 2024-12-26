from flask import Flask, request, Response, stream_with_context, render_template_string
from playwright.sync_api import sync_playwright
import time
import re

app = Flask(__name__)

# ╔══════════════════════════════════╗
# ║                                             
# ║    𝗖𝗼𝗽𝘆𝗿𝗶𝗴𝗵𝘁 © 𝟮𝟬𝟮𝟰 𝗬𝗨𝗩𝗥𝗔𝗝𝗠𝗢𝗗𝗭     
# ║     𝗖𝗥𝗘𝗗𝗜𝗧: 𝐌𝐀𝐓𝐑𝐈𝐗 𝐃𝐄𝐕𝐄𝐋𝐎𝐏𝐄𝐑      
# ║                                            
# ╚══════════════════════════════════╝

def is_valid_spotify_url(url):
    # Regex to validate Spotify links
    spotify_pattern = re.compile(r"https://open\.spotify\.com/(artist|track|album|playlist|show|episode)/[a-zA-Z0-9]+")
    return bool(spotify_pattern.match(url))

def scrape_and_stream_links(spotify_url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        page.goto("https://spowload.com")
        page.wait_for_selector("input[name=\"trackUrl\"]")
        page.fill("input[name=\"trackUrl\"]", spotify_url)
        time.sleep(1)
        page.click("button#btnSubmit")
        page.wait_for_load_state("networkidle")
        song_divs = page.query_selector_all("div.row.align-items-center.border-bottom")

        for song_div in song_divs:
            try:
                song_name = song_div.query_selector("div.col-7 p").inner_text().strip()
                convert_button = song_div.query_selector("button.btn.btn-light")
                convert_button.click()
                page.wait_for_selector(".progress-bar")
                page.wait_for_selector(".progress-bar", state="detached")
                download_link = song_div.query_selector("a[href]")

                if download_link:
                    download_url = download_link.get_attribute("href")
                    yield f'<div style="margin-bottom: 10px;"><button onclick="window.location.href=\'{download_url}\'" style="padding: 10px 20px; font-size: 14px;">Click to download: {song_name}</button></div>'
                time.sleep(1)
            except Exception as e:
                yield f"<p>Error processing a song: {str(e)}</p>"

        browser.close()

@app.route("/")
def home():
    html_page = """
    <!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no">
    <title>Spot-Tube</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .fade-in {
            animation: fadeIn 1s ease;
        }
        .floating-label {
            transition: all 0.3s ease;
            top: 50%;
            transform: translateY(-50%);
        }
        input:focus + .floating-label,
        input:not(:placeholder-shown) + .floating-label {
            top: 0;
            transform: translateY(-50%) scale(0.85);
            background-color: white;
            padding: 0 4px;
            color: #10B981;
        }
    </style>
</head>
<body class="bg-gray-100 font-sans">
    <button id="menuToggle" class="fixed top-5 right-5 z-50 text-2xl bg-green-500 text-white p-2 rounded-full shadow-lg hover:bg-green-600 transition-colors duration-300">☰</button>
    
    <div id="sidebar" class="fixed top-0 right-0 w-3/4 md:w-1/3 h-full bg-green-500 text-white p-6 shadow-lg transform translate-x-full transition-transform duration-300 ease-in-out z-40">
        <button id="closeSidebar" class="absolute top-4 right-4 text-2xl hover:text-gray-200 transition-colors duration-300">&times;</button>
        <nav class="flex flex-col space-y-4 mt-12">
            <a href="https://t.me/matrix_env" class="bg-white text-green-500 py-2 px-4 rounded-lg text-center font-semibold hover:bg-gray-100 transition-colors duration-300">JOIN TELEGRAM CHANNEL</a>
            <a href="https://t.me/vzr7x" class="bg-white text-green-500 py-2 px-4 rounded-lg text-center font-semibold hover:bg-gray-100 transition-colors duration-300">CONTACT</a>
        </nav>
    </div>

    <div class="min-h-screen flex justify-center items-center p-4">
        <div class="bg-white p-8 rounded-xl shadow-2xl max-w-md w-full fade-in">
            <h1 class="text-3xl font-bold text-center text-green-500 mb-6">Spot-Tube</h1>
            <form id="spotify-form">
                <div class="relative mb-4">
                    <input type="url" id="url" name="url" placeholder=" " required class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent transition-all duration-300 bg-gray-50 peer">
                    <label for="url" class="floating-label absolute left-3 text-gray-500 pointer-events-none">Enter Spotify URL</label>
                </div>
                <button type="submit" class="w-full bg-green-500 text-white py-2 px-4 rounded-md hover:bg-green-600 transition-colors duration-300">Proceed</button>
            </form>
            <div id="results" class="mt-4"></div>
        </div>
    </div>

    <script>
        const menuToggle = document.getElementById('menuToggle');
        const sidebar = document.getElementById('sidebar');
        const closeSidebar = document.getElementById('closeSidebar');
        const mainContent = document.querySelector('.min-h-screen');

        function toggleSidebar() {
            sidebar.classList.toggle('translate-x-full');
            if (!sidebar.classList.contains('translate-x-full')) {
                mainContent.style.transform = 'translateX(-16.66%)';
            } else {
                mainContent.style.transform = 'translateX(0)';
            }
        }

        menuToggle.addEventListener('click', toggleSidebar);
        closeSidebar.addEventListener('click', toggleSidebar);

        document.getElementById('spotify-form').onsubmit = async function(event) {
            event.preventDefault();
            const form = event.target;
            const url = form.url.value;
            const resultsDiv = document.getElementById('results');
            resultsDiv.innerHTML = '<div class="flex justify-center items-center space-x-2"><div class="w-2 h-2 bg-green-500 rounded-full animate-bounce"></div><div class="w-2 h-2 bg-green-500 rounded-full animate-bounce" style="animation-delay: -0.3s"></div><div class="w-2 h-2 bg-green-500 rounded-full animate-bounce" style="animation-delay: -0.5s"></div></div>';

            try {
                const response = await fetch(`/spotify?url=${encodeURIComponent(url)}`);
                const text = await response.text();
                resultsDiv.innerHTML = text;
            } catch (error) {
                resultsDiv.innerHTML = '<p class="text-red-500">Error fetching data. Please try again later.</p>';
            }
        };
    </script>
</body>
</html>
    """
    return render_template_string(html_page)

@app.route("/spotify", methods=["GET"])
def spotify_handler():
    spotify_url = request.args.get("url")
    if not spotify_url:
        return "Error: No Spotify URL provided.", 400

    if not is_valid_spotify_url(spotify_url):
        return "Error: Invalid Spotify URL provided. Please use a valid Spotify link.", 400

    return Response(
        stream_with_context(scrape_and_stream_links(spotify_url)),
        mimetype="text/html"
    )

if __name__ == "__main__":
    app.run(debug=True)
