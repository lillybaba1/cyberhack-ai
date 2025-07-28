import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { BarChart, Bar, XAxis, YAxis } from 'recharts';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import axios from 'axios';  // Add to package.json: "axios": "^1.7.2"

const Dashboard: React.FC = () => {
  const [target, setTarget] = useState('');
  const [results, setResults] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const handleScan = async () => {
    setLoading(true);
    try {
      const res = await axios.post('http://localhost:8000/scans/vuln', null, { params: { target } });
      setResults(res.data);
    } catch (err) {
      console.error(err);
    }
    setLoading(false);
  };

  const handlePlaybook = async () => {
    setLoading(true);
    try {
      const res = await axios.post('http://localhost:8000/scans/playbook/run', null, { params: { playbook_name: 'web_app_flow.yaml' } });
      setResults(res.data);
    } catch (err) {
      console.error(err);
    }
    setLoading(false);
  };

  const chartData = results ? [{ name: 'Risk', value: results.risk_score }] : [{ name: 'Vulns', value: 10 }];

  return (
    <div className="p-4">
      <Card>
        <CardHeader>
          <CardTitle>Vulnerability Dashboard</CardTitle>
        </CardHeader>
        <CardContent>
          <Input 
            placeholder="Enter target (e.g., example.com)" 
            value={target} 
            onChange={(e) => setTarget(e.target.value)} 
          />
          <Button onClick={handleScan} disabled={loading}>Run Scan</Button>
          <Button onClick={handlePlaybook} disabled={loading}>Run Web Playbook</Button>
          {loading && <p>Scanning...</p>}
          {results && (
            <>
              <pre>{JSON.stringify(results.results, null, 2)}</pre>  {/* Real-time: Use WebSockets later */}
              <BarChart width={600} height={300} data={chartData}>
                <XAxis dataKey="name" />
                <YAxis />
                <Bar dataKey="value" fill="#8884d8" />
              </BarChart>
            </>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default Dashboard;