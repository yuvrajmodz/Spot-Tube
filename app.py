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
    <title>Spot-Tube Pro</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <script>
        tailwind.config = {
            theme: {
                extend: {
                    colors: {
                        primary: '#6366F1',
                        secondary: '#EC4899',
                        accent: '#8B5CF6',
                        background: '#F3F4F6',
                    },
                    fontFamily: {
                        sans: ['Inter', 'sans-serif'],
                    },
                }
            }
        }
    </script>
    <style>
        @keyframes gradient {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }
        .gradient-bg {
            background: linear-gradient(-45deg, #6366F1, #EC4899, #8B5CF6, #10B981);
            background-size: 400% 400%;
            animation: gradient 15s ease infinite;
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
            color: #6366F1;
        }
    </style>
</head>
<body class="bg-background font-sans text-gray-800">
    <div class="fixed top-0 left-0 w-full h-1 gradient-bg"></div>
    
    <button id="menuToggle" class="fixed top-5 right-5 z-50 bg-white text-primary p-2 rounded-full shadow-lg hover:shadow-xl transition-all duration-300 transform hover:scale-110 focus:outline-none focus:ring-2 focus:ring-primary focus:ring-opacity-50">
        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16m-7 6h7"></path>
        </svg>
    </button>
    
    <div id="sidebar" class="fixed top-0 right-0 w-3/4 md:w-1/3 h-full bg-white text-gray-800 p-6 shadow-2xl transform translate-x-full transition-transform duration-500 ease-in-out z-40">
        <nav class="flex flex-col space-y-4 mt-16">
            <a href="https://t.me/matrix_env" class="bg-primary text-white py-3 px-6 rounded-lg text-center font-semibold hover:bg-opacity-90 transition-all duration-300 transform hover:scale-105 shadow-md">JOIN TELEGRAM CHANNEL</a>
            <a href="https://t.me/vzr7x" class="bg-secondary text-white py-3 px-6 rounded-lg text-center font-semibold hover:bg-opacity-90 transition-all duration-300 transform hover:scale-105 shadow-md">CONTACT</a>
        </nav>
    </div>

    <div class="min-h-screen flex justify-center items-center p-4 bg-gradient-to-br from-blue-50 to-pink-50">
        <div class="bg-white p-8 rounded-3xl shadow-xl max-w-md w-full transform transition-all duration-500 hover:shadow-2xl">
            <div class="flex items-center justify-center mb-8">
                <svg class="w-12 h-12 text-primary mr-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3"></path>
                </svg>
                <h1 class="text-4xl font-bold text-gray-800">Spot-Tube Pro</h1>
            </div>
            <form id="spotify-form" class="space-y-6">
                <div class="relative">
                    <input type="url" id="url" name="url" placeholder=" " required class="w-full px-4 py-3 bg-gray-50 border-2 border-gray-200 rounded-lg focus:outline-none focus:border-primary transition-all duration-300 text-gray-800">
                    <label for="url" class="floating-label absolute left-4 text-gray-500 pointer-events-none">Enter Spotify URL</label>
                </div>
                <button type="submit" class="w-full bg-primary text-white py-3 px-6 rounded-lg hover:bg-opacity-90 transition-all duration-300 transform hover:scale-105 focus:outline-none focus:ring-2 focus:ring-primary focus:ring-opacity-50 shadow-lg">
                    Download Playlist
                </button>
            </form>
            <div id="results" class="mt-6"></div>
        </div>
    </div>

    <script>
        const menuToggle = document.getElementById('menuToggle');
        const sidebar = document.getElementById('sidebar');
        const mainContent = document.querySelector('.min-h-screen');

        function toggleSidebar() {
            sidebar.classList.toggle('translate-x-full');
            mainContent.classList.toggle('scale-95');
            mainContent.classList.toggle('blur-sm');
        }

        menuToggle.addEventListener('click', toggleSidebar);

        document.getElementById('spotify-form').onsubmit = async function(event) {
            event.preventDefault();
            const form = event.target;
            const url = form.url.value;
            const resultsDiv = document.getElementById('results');
            resultsDiv.innerHTML = `
                <div class="flex justify-center items-center space-x-2 py-4">
                    <div class="w-3 h-3 bg-primary rounded-full animate-bounce"></div>
                    <div class="w-3 h-3 bg-secondary rounded-full animate-bounce" style="animation-delay: -0.3s"></div>
                    <div class="w-3 h-3 bg-accent rounded-full animate-bounce" style="animation-delay: -0.5s"></div>
                </div>
            `;

            try {
                const response = await fetch(`/spotify?url=${encodeURIComponent(url)}`);
                const text = await response.text();
                resultsDiv.innerHTML = `
                    <div class="bg-gray-50 p-6 rounded-lg shadow-inner">
                        <h3 class="text-lg font-semibold text-gray-800 mb-2">RESULT</h3>
                        <p class="text-gray-600">${text.replace(/Click to download:/g, '<span class="text-blue-500 font-medium">Click to download:</span>')}</p>
                    </div>
                `;
            } catch (error) {
                resultsDiv.innerHTML = `
                    <div class="bg-red-50 p-6 rounded-lg shadow-inner">
                        <h3 class="text-lg font-semibold text-red-800 mb-2">Error:</h3>
                        <p class="text-red-600">Unable to fetch data. Please try again later.</p>
                    </div>
                `;
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
