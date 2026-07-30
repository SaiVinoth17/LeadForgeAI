import re

with open('command_center.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Remove sidebar HTML
html = re.sub(r'<aside class="sidebar">.*?</aside>', '', html, flags=re.DOTALL)

# Adjust shell grid
html = html.replace('grid-template-columns:76px 1fr;', 'grid-template-columns:1fr;')

# Add a script block for fetching data
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
</script>
"""

# Append script to body
html = html.replace('</body>', fetch_script + '\n</body>')

with open('command_center.html', 'w', encoding='utf-8') as f:
    f.write(html)
