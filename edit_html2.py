import re

with open('command_center.html', 'r', encoding='utf-8') as f:
    html = f.read()

# We want to replace the static <div class="feed-row"> elements with an empty container we can populate.
# But since we want to preserve animations, we will just use regex to strip out the existing feed-row blocks and inject an empty div.

html = re.sub(r'<div class="feed-row">.*?</div>\s*</div>\s*<div class="feed-row">', '<div class="feed-row">', html, flags=re.DOTALL)
# Basically, let's just find the first feed-row and slice up to it.
start = html.find('<div class="feed-row">')
if start != -1:
    end = html.rfind('</div>', 0, html.find('</div>', html.find('</div>', html.find('<div class="feed-row">')))) # this is brittle.
    
# Let's replace the script instead to also fetch the feed.
fetch_script = """
<script>
async function updateData() {
    try {
        const response = await fetch('http://127.0.0.1:49281/api/kpis');
        if (response.ok) {
            const data = await response.json();
            
            const kpiEls = document.querySelectorAll('[data-count]');
            if (kpiEls.length >= 4) {
                // Assuming order: Leads, Scrapers, Accuracy, Credits
                kpiEls[0].setAttribute('data-count', data.leads_forged);
                kpiEls[1].setAttribute('data-count', data.active_scrapers);
                kpiEls[2].setAttribute('data-count', data.accuracy);
                kpiEls[3].setAttribute('data-count', data.credits);
                
                // Restart animations
                kpiEls.forEach(el => {
                    const target = parseFloat(el.getAttribute('data-count'));
                    const obj = {val: 0};
                    gsap.to(obj, {
                        val: target, duration: 1.6, ease: 'power2.out', delay: 0.1,
                        onUpdate: () => {
                            el.childNodes[0].nodeValue = Math.round(obj.val).toLocaleString();
                        }
                    });
                });
            }
            
            // Update Feed
            const feedContainer = document.getElementById('liveFeedContainer');
            if (feedContainer && data.recent_leads) {
                feedContainer.innerHTML = '';
                data.recent_leads.forEach((lead, i) => {
                    const initials = lead.name.substring(0, 2).toUpperCase();
                    const scoreClass = lead.score >= 85 ? 'score-hot' : 'score-warm';
                    const scoreText = lead.score >= 85 ? 'HOT' : 'WARM';
                    
                    const row = document.createElement('div');
                    row.className = 'feed-row';
                    row.innerHTML = `
                        <div class="feed-avatar">${initials}</div>
                        <div>
                          <div class="feed-name">${lead.name}</div>
                          <div class="feed-meta">${lead.website || 'No website'}</div>
                        </div>
                        <div class="feed-score ${scoreClass}">${lead.score} ${scoreText}</div>
                        <div class="feed-time">Just now</div>
                    `;
                    feedContainer.appendChild(row);
                });
                
                gsap.from('#liveFeedContainer .feed-row', {
                  opacity:0, x:-14, stagger:0.08, duration:0.5, delay:0.2, ease:'power2.out'
                });
            }
        }
    } catch (e) {
        console.error("Error fetching KPIs:", e);
    }
}

// Call updateData initially and every 10s
updateData();
setInterval(updateData, 10000);

document.getElementById('launchBtn').addEventListener('click', async () => {
    try {
        const targetQuery = document.querySelector('.field').value;
        await fetch('http://127.0.0.1:49281/api/launch', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({query: targetQuery})
        });
    } catch (e) {}
});
document.getElementById('runScrapeBtn').addEventListener('click', async () => {
    try {
        await fetch('http://127.0.0.1:49281/api/launch', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({query: ''})
        });
    } catch (e) {}
});
</script>
"""

# Let's cleanly replace the live feed stream block
# Find `<div class="feed-row">` and replace all siblings up to `</div>\n        </div>`
block_regex = r'<div class="feed-row">.*?(?=<div class="panel reveal">)'
html = re.sub(block_regex, '<div id="liveFeedContainer"></div>\n        </div>\n\n        ', html, flags=re.DOTALL)

# Now replace the script block
html = re.sub(r'<script>.*?</script>', fetch_script, html, flags=re.DOTALL)

with open('command_center.html', 'w', encoding='utf-8') as f:
    f.write(html)
