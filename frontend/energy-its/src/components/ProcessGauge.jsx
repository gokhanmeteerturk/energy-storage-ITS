// src/components/ProgressGauge.jsx
import { PieChart, Pie, Cell, ResponsiveContainer, Label } from 'recharts';
import { Paper, Typography, Box } from '@mui/material';

export function ProgressGauge({ topicHierarchy }) {
  // This function recursively counts all topics and completed topics
  const countProgress = (topics) => {
    let total = 0;
    let completed = 0;

    const processNode = (node) => {
      total += 1;
      if (node.status === 'passed') {
        completed += 1;
      }
      if (node.children) {
        node.children.forEach(processNode);
      }
    };

    topics.forEach(processNode);
    return { total, completed };
  };

  const { total, completed } = countProgress(topicHierarchy);
  const percentage = total > 0 ? Math.round((completed / total) * 100) : 0;

  // Prepare data for the pie chart
  const data = [
    { value: percentage },
    { value: 100 - percentage }
  ];

  return (
    <Paper 
      elevation={3} 
      sx={{ 
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        p: 2
      }}
    >
      <Typography variant="h6" gutterBottom>
        Your Progress
      </Typography>
      
      <Box sx={{ width: '100%', height: 200 }}>
        <ResponsiveContainer>
          <PieChart>
            <Pie
              data={data}
              innerRadius={60}
              outerRadius={80}
              startAngle={90}
              endAngle={450}
              dataKey="value"
            >
              <Cell fill="#4caf50" />
              <Cell fill="#e0e0e0" />
              <Label
                value={`${percentage}%`}
                position="center"
                style={{
                  fontSize: '24px',
                  fontWeight: 'bold',
                  fill: '#000000'
                }}
              />
            </Pie>
          </PieChart>
        </ResponsiveContainer>
      </Box>

      <Typography variant="body2" color="text.secondary" align="center">
        {completed} of {total} topics completed
      </Typography>
    </Paper>
  );
}
