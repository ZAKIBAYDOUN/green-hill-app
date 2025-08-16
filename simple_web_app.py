"""
Simple web interface for testing the Green Hill strategic agent system
"""
from flask import Flask, render_template_string, request, jsonify
from main import build_graph
import json
import time

app = Flask(__name__)
graph_app = build_graph()

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>🎯 Green Hill Strategic Agent Test</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 1200px; margin: 0 auto; padding: 20px; }
        .header { background: linear-gradient(135deg, #2E8B57, #228B22); color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px; }
        .test-section { background: #f8f9fa; padding: 20px; border-radius: 10px; margin-bottom: 20px; }
        .input-group { margin-bottom: 15px; }
        label { display: block; margin-bottom: 5px; font-weight: bold; }
        input, textarea { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 5px; }
        button { background: #2E8B57; color: white; padding: 12px 24px; border: none; border-radius: 5px; cursor: pointer; }
        button:hover { background: #228B22; }
        .result { background: white; border: 1px solid #ddd; border-radius: 5px; padding: 15px; margin-top: 15px; }
        .agent-flow { display: flex; flex-wrap: wrap; gap: 10px; margin: 10px 0; }
        .agent-step { background: #e8f5e8; padding: 8px 12px; border-radius: 5px; font-size: 12px; }
        .artifact { background: #f0f8ff; padding: 10px; border-radius: 5px; margin: 5px 0; }
        .loading { color: #666; font-style: italic; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🎯 Green Hill Strategic Agent Core</h1>
        <p>Clean deployment test interface - Full agent autonomy enabled</p>
    </div>

    <div class="test-section">
        <h2>🧪 Strategic Intelligence Testing</h2>
        <div class="input-group">
            <label for="question">Business Question or Strategic Query:</label>
            <textarea id="question" rows="3" placeholder="e.g., What is the 9-month plan to reach EU-GMP with ROI > 20%?">What is the strategic plan for Green Hill Canarias?</textarea>
        </div>
        <div class="input-group">
            <label for="thread-id">Thread ID (for conversation continuity):</label>
            <input type="text" id="thread-id" value="test-session-1" placeholder="test-session-1">
        </div>
        <button onclick="runTest()">🚀 Execute Strategic Analysis</button>
        
        <div id="result" class="result" style="display: none;">
            <h3>📊 Analysis Results</h3>
            <div id="loading" class="loading">Processing through agent chain...</div>
            <div id="agent-flow" class="agent-flow"></div>
            <div id="final-answer"></div>
            <div id="artifacts"></div>
        </div>
    </div>

    <script>
        async function runTest() {
            const question = document.getElementById('question').value;
            const threadId = document.getElementById('thread-id').value;
            const resultDiv = document.getElementById('result');
            const loadingDiv = document.getElementById('loading');
            const agentFlowDiv = document.getElementById('agent-flow');
            const finalAnswerDiv = document.getElementById('final-answer');
            const artifactsDiv = document.getElementById('artifacts');
            
            resultDiv.style.display = 'block';
            loadingDiv.style.display = 'block';
            agentFlowDiv.innerHTML = '';
            finalAnswerDiv.innerHTML = '';
            artifactsDiv.innerHTML = '';
            
            try {
                const response = await fetch('/test', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({question: question, thread_id: threadId})
                });
                
                const result = await response.json();
                loadingDiv.style.display = 'none';
                
                if (result.success) {
                    // Show agent flow
                    const agents = result.history || [];
                    agents.forEach(msg => {
                        const step = document.createElement('div');
                        step.className = 'agent-step';
                        step.textContent = `${msg.role}: ${msg.content}`;
                        agentFlowDiv.appendChild(step);
                    });
                    
                    // Show final answer
                    finalAnswerDiv.innerHTML = `<h4>🎯 Final Strategic Assessment:</h4><p><strong>${result.final_answer}</strong></p>`;
                    
                    // Show artifacts
                    let artifactsHtml = '<h4>📋 Strategic Artifacts Generated:</h4>';
                    if (result.plan) artifactsHtml += `<div class="artifact"><strong>Strategic Plan:</strong> ${JSON.stringify(result.plan)}</div>`;
                    if (result.financials) artifactsHtml += `<div class="artifact"><strong>Financial Model:</strong> ${JSON.stringify(result.financials)}</div>`;
                    if (result.schedule) artifactsHtml += `<div class="artifact"><strong>Timeline:</strong> ${JSON.stringify(result.schedule)}</div>`;
                    if (result.capex_breakdown) artifactsHtml += `<div class="artifact"><strong>CapEx Breakdown:</strong> ${JSON.stringify(result.capex_breakdown)}</div>`;
                    if (result.quality_gaps) artifactsHtml += `<div class="artifact"><strong>Quality Gaps:</strong> ${JSON.stringify(result.quality_gaps)}</div>`;
                    if (result.regulatory_actions) artifactsHtml += `<div class="artifact"><strong>Regulatory Actions:</strong> ${JSON.stringify(result.regulatory_actions)}</div>`;
                    
                    artifactsDiv.innerHTML = artifactsHtml;
                } else {
                    finalAnswerDiv.innerHTML = `<p style="color: red;">❌ Error: ${result.error}</p>`;
                }
            } catch (error) {
                loadingDiv.style.display = 'none';
                finalAnswerDiv.innerHTML = `<p style="color: red;">❌ Network error: ${error.message}</p>`;
            }
        }
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/test', methods=['POST'])
def test_agent():
    try:
        data = request.json
        question = data.get('question', 'What is the strategic plan?')
        thread_id = data.get('thread_id', 'default')
        
        start_time = time.time()
        result = graph_app.invoke(
            {'question': question}, 
            {'configurable': {'thread_id': thread_id}}
        )
        execution_time = time.time() - start_time
        
        return jsonify({
            'success': True,
            'final_answer': result.get('final_answer'),
            'plan': result.get('plan'),
            'financials': result.get('financials'),
            'schedule': result.get('schedule'),
            'capex_breakdown': result.get('capex_breakdown'),
            'quality_gaps': result.get('quality_gaps'),
            'regulatory_actions': result.get('regulatory_actions'),
            'history': [{'role': msg.role, 'content': msg.content} for msg in result.get('history', [])],
            'execution_time': execution_time,
            'notes': result.get('notes', [])
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    print("🎯 GREEN HILL STRATEGIC AGENT TEST INTERFACE")
    print("=" * 50)
    print("🌐 Starting test interface on http://localhost:5000")
    print("🧪 Ready for exhaustive testing!")
    app.run(host='0.0.0.0', port=5000, debug=True)
