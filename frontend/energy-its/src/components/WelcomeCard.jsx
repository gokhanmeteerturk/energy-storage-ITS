// src/components/WelcomeCard.jsx
import { Paper, Typography, Box } from '@mui/material';

export function WelcomeCard({ topicHierarchy }) {
  // Function to determine the next recommended action
  const getNextAction = (topics) => {
    let nextAction = '';
    
    // Helper function to find the first incomplete topic
    const findIncomplete = (nodes) => {
      for (const node of nodes) {
        if (node.status !== 'passed') {
          return node;
        }
        if (node.children) {
          const incomplete = findIncomplete(node.children);
          if (incomplete) return incomplete;
        }
      }
      return null;
    };

    const nextTopic = findIncomplete(topics);
    
    if (!nextTopic) {
      return "Congratulations! You've completed all topics. Feel free to review any topic by clicking 'Retake'.";
    }

    return `We recommend starting with "${nextTopic.id.replace(/([A-Z])/g, ' $1').trim()}" next.`;
  };

  return (
    <Paper 
      elevation={3} 
      sx={{ 
        height: '100%',
        p: 3,
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'space-between'
      }}
    >
      <Box>
        <Typography variant="h4" gutterBottom>
          Welcome to the Energy Storage Systems ITS Module
        </Typography>
        
        <Typography paragraph>
          This intelligent tutoring system will guide you through understanding various energy storage technologies.
          Each topic contains detailed explanations, interactive elements, and quizzes to test your knowledge.
          Complete parent topics to unlock their sub-topics and track your progress as you learn.
        </Typography>

        <Typography variant="subtitle1" sx={{ mt: 2, fontWeight: 'bold' }}>
          Next Steps
        </Typography>
        
        <Typography>
          {getNextAction(topicHierarchy)}
        </Typography>
      </Box>
    </Paper>
  );
}
