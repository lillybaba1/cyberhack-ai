import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { BarChart, Bar, XAxis, YAxis } from 'recharts';

const data = [{ name: 'Vulns', value: 10 }, { name: 'Fixed', value: 5 }];

const Dashboard: React.FC = () => {
  return (
    <div className="p-4">
      <Card>
        <CardHeader>
          <CardTitle>Vulnerability Summary</CardTitle>
        </CardHeader>
        <CardContent>
          <BarChart width={600} height={300} data={data}>
            <XAxis dataKey="name" />
            <YAxis />
            <Bar dataKey="value" fill="#8884d8" />
          </BarChart>
        </CardContent>
      </Card>
    </div>
  );
};

export default Dashboard;
