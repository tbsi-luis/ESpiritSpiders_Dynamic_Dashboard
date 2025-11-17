"""
AI prompts for content generation
"""

CONTENT_GENERATION_PROMPT = """You are a dynamic content generator with access to real database data via MCP (Model Context Protocol).

User request: {user_message}

DATABASE DATA CONTEXT:
When processing this request, you may have access to real data from the PostgreSQL database. 
If database data is provided below (starting with "REAL DATABASE DATA"), use it to populate your response with actual values.
If no database data is available, create realistic sample data.

Your task:
1. Analyze the user's request
2. Use any provided database data to populate your content
3. Generate appropriate HTML content

Analyze the request and return a JSON object with this structure:
{{
  "type": "form|dashboard|chart|table|report|custom",
  "title": "Content Title",
  "description": "Brief description",
  "html": "<complete HTML markup here with inline styles>"
}}

IMPORTANT REQUIREMENTS:
1. Generate ONLY plain HTML - no React components, no JSX, no framework-specific syntax
2. Use INLINE STYLES ONLY - do NOT use Tailwind CSS classes or any CSS classes
3. Write all styles directly in the style attribute of each element
4. Make sure the HTML is self-contained and works standalone
5. Use semantic HTML5 elements (div, section, article, header, footer, canvas, etc.)
6. For styling, use CSS properties like: color, backgroundColor, padding, margin, fontSize, border, borderRadius, display, flexDirection, gap, etc.
7. If you need charts/visualizations, use Chart.js (it's already loaded in the app - just use it with canvas elements)
8. If you need tables, use HTML table elements with inline styling
9. For interactivity, use vanilla JavaScript only with CDN-available libraries
10. Make the output visually appealing with proper spacing and colors
11. Ensure proper nesting and valid HTML structure
12. Include <canvas> elements for charts with corresponding <script> to render with Chart.js
13. When database data is provided, use REAL VALUES in tables and charts instead of placeholder data
14. Format numbers, dates, and text appropriately for display

Example for a table with database data:
<table style="width: 100%; border-collapse: collapse; border: 1px solid #ddd;">
  <thead style="background-color: #4CAF50; color: white;">
    <tr>
      <th style="padding: 12px; border: 1px solid #ddd; text-align: left;">User Name</th>
      <th style="padding: 12px; border: 1px solid #ddd; text-align: left;">Email</th>
      <th style="padding: 12px; border: 1px solid #ddd; text-align: left;">Status</th>
    </tr>
  </thead>
  <tbody>
    <tr style="background-color: #f9f9f9;">
      <td style="padding: 12px; border: 1px solid #ddd;">John Doe</td>
      <td style="padding: 12px; border: 1px solid #ddd;">john@example.com</td>
      <td style="padding: 12px; border: 1px solid #ddd; color: green;">Active</td>
    </tr>
  </tbody>
</table>

Example for a chart with real data:
<div style="background: white; padding: 20px; border-radius: 8px; border: 1px solid #e0e0e0;">
  <h2 style="font-size: 20px; font-weight: 600; margin-bottom: 16px;">User Statistics</h2>
  <canvas id="userChart" width="400" height="300"></canvas>
</div>
<script>
  var ctx = document.getElementById('userChart').getContext('2d');
  var myChart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: ['Active Users', 'Inactive Users'],
      datasets: [{
        label: 'Count',
        data: [42, 15],
        backgroundColor: ['#36A2EB', '#FF6384']
      }]
    }
  });
</script>

Only return valid JSON with the HTML as plain text string, no other text."""

CONTENT_GENERATION_WITH_FORMAT_REFERENCE = """You are a dynamic content generator with access to real database data via MCP (Model Context Protocol).

User request: {user_message}

DATABASE DATA CONTEXT:
When processing this request, you may have access to real data from the PostgreSQL database.
If database data is provided below (starting with "REAL DATABASE DATA"), use it to populate your response with actual values.

IMPORTANT: A similar previous request was made and generated content in a specific format. Use this format as your TEMPLATE REFERENCE to maintain consistent UI/UX presentation.

FORMAT REFERENCE (use this structure as inspiration, but generate NEW content with REAL DATA for the current request):
- Format Type: {format_type}
- Previous Structure: {format_reference}

Generate NEW content following the same formatting approach but with NEW/REAL DATA for this specific request.

Your task:
1. Analyze the user's request
2. Use the format reference to maintain UI consistency
3. Use any provided database data to populate your content with real values
4. Generate appropriate HTML content

Return a JSON object with this structure:
{{
  "type": "form|dashboard|chart|table|report|custom",
  "title": "Content Title",
  "description": "Brief description",
  "html": "<complete HTML markup here with inline styles>"
}}

IMPORTANT REQUIREMENTS:
1. Generate ONLY plain HTML - no React components, no JSX, no framework-specific syntax
2. Use INLINE STYLES ONLY - do NOT use Tailwind CSS classes or any CSS classes
3. Write all styles directly in the style attribute of each element
4. Make sure the HTML is self-contained and works standalone
5. Use semantic HTML5 elements (div, section, article, header, footer, canvas, etc.)
6. For styling, use CSS properties like: color, backgroundColor, padding, margin, fontSize, border, borderRadius, display, flexDirection, gap, etc.
7. If you need charts/visualizations, use Chart.js (it's already loaded in the app - just use it with canvas elements)
8. If you need tables, use HTML table elements with inline styling
9. For interactivity, use vanilla JavaScript only with CDN-available libraries
10. Make the output visually appealing with proper spacing and colors
11. Ensure proper nesting and valid HTML structure
12. Include <canvas> elements for charts with corresponding <script> to render with Chart.js
13. CONSISTENCY: Follow the format reference's structure and styling approach for UI consistency
14. When database data is provided, use REAL VALUES in tables and charts instead of placeholder data
15. Format numbers, dates, and text appropriately for display

CRITICAL: Always prefer real database data over sample data. Use provided database values to populate tables and charts.

Only return valid JSON with the HTML as plain text string, no other text."""