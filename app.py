import time
import urllib.request
import xml.etree.ElementTree as ET
from flask import Flask, jsonify, render_template, send_from_directory

app = Flask(__name__, static_folder='static', template_folder='templates')

# Memory cache for release notes to avoid hitting the endpoint too frequently
cache = {
    'data': None,
    'timestamp': 0
}
CACHE_TTL = 300  # 5 minutes

def parse_xml_feed(xml_data):
    root = ET.fromstring(xml_data)
    ns = {'atom': 'http://www.w3.org/2005/Atom'}
    
    entries = root.findall('.//atom:entry', ns)
    if not entries:
        entries = root.findall('.//entry')
        
    parsed_entries = []
    for entry in entries:
        title_el = entry.find('atom:title', ns)
        if title_el is None:
            title_el = entry.find('title')
            
        updated_el = entry.find('atom:updated', ns)
        if updated_el is None:
            updated_el = entry.find('updated')
            
        id_el = entry.find('atom:id', ns)
        if id_el is None:
            id_el = entry.find('id')
            
        content_el = entry.find('atom:content', ns)
        if content_el is None:
            content_el = entry.find('content')
        
        # Link element can be multiple or have different formats, let's extract the href
        link_href = ""
        link_el = entry.find('atom:link', ns)
        if link_el is None:
            link_el = entry.find('link')
        if link_el is not None:
            link_href = link_el.attrib.get('href', '')
            
        title = title_el.text if title_el is not None else ""
        updated = updated_el.text if updated_el is not None else ""
        entry_id = id_el.text if id_el is not None else ""
        content = content_el.text if content_el is not None else ""
        
        parsed_entries.append({
            'id': entry_id,
            'title': title,
            'updated': updated,
            'link': link_href,
            'content': content
        })
        
    return parsed_entries

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/release-notes')
def get_release_notes():
    global cache
    now = time.time()
    
    # Check cache
    if cache['data'] and (now - cache['timestamp'] < CACHE_TTL):
        return jsonify({
            'success': True,
            'source': 'cache',
            'data': cache['data']
        })
        
    url = "https://docs.cloud.google.com/feeds/bigquery-release-notes.xml"
    try:
        req = urllib.request.Request(
            url,
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            xml_data = response.read()
            
        notes = parse_xml_feed(xml_data)
        
        # Update cache
        cache['data'] = notes
        cache['timestamp'] = now
        
        return jsonify({
            'success': True,
            'source': 'network',
            'data': notes
        })
    except Exception as e:
        # Return cache if network fails, otherwise return error
        if cache['data']:
            return jsonify({
                'success': True,
                'source': 'cache_fallback_after_error',
                'data': cache['data'],
                'error': str(e)
            })
        return jsonify({
            'success': False,
            'error': f"Failed to fetch release notes: {str(e)}"
        }), 500

if __name__ == '__main__':
    # Running locally on port 5000
    app.run(host='127.0.0.1', port=5000, debug=True)
