// src/components/TopicList.jsx
import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  Typography,
  Paper,
  Card,
  CardContent,
  CardActions,
  Button,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Grid,
  Chip
} from '@mui/material';
import { Lock, PlayArrow, Refresh } from '@mui/icons-material';
import axios from 'axios';
import { WelcomeCard } from './WelcomeCard';
import { ProgressGauge } from './ProcessGauge';


function isTopicAvailable(topic, allTopics) {
  // If it's a top-level topic (no parent), it's available if marked as such
  if (!topic.parentId) {
    return topic.available;
  }

  // Find the parent topic
  const findParentTopic = (topicId, topics) => {
    for (const t of topics) {
      if (t.id === topicId) return t;
      if (t.children) {
        const found = findParentTopic(topicId, t.children);
        if (found) return found;
      }
    }
    return null;
  };

  const parent = findParentTopic(topic.parentId, allTopics);
  
  // Topic is only available if:
  // 1. It's marked as available (prerequisites met)
  // 2. Its parent exists and has been passed
  return topic.available && parent && parent.status === 'passed';
}


// This function recursively checks the status of all subtopics
function getTopicProgress(topic) {
  // If there are no children, just return the topic's own status
  if (!topic.children || topic.children.length === 0) {
    return topic.status;
  }

  // Check all children recursively
  const childStatuses = topic.children.map(getTopicProgress);
  
  // If all children are passed, return passed
  if (childStatuses.every(status => status === 'passed')) {
    return 'passed';
  }
  
  // If any child is passed or has status, return ongoing
  if (childStatuses.some(status => status === 'passed' || status === 'failed')) {
    return 'ongoing';
  }
  
  // If we get here, all children are not_started
  return 'not_started';
}

// This function counts all descendants of a topic
function countDescendants(topic) {
  if (!topic.children || topic.children.length === 0) {
    return 0;
  }
  return topic.children.length + topic.children.reduce((acc, child) => 
    acc + countDescendants(child), 0
  );
}

// This function determines the button text for a topic
function getActionButtonText(topic) {
  if (!topic.available) {
    return 'Locked';
  }

  const progress = getTopicProgress(topic);
  switch (progress) {
    case 'passed':
      return 'Retake';
    case 'ongoing':
      return 'Continue';
    default:
      return 'Start';
  }
}
function StatusChip({ status }) {
  const getStatusProps = (status) => {
    switch (status) {
      case 'not_started':
        return { label: 'Not Started', color: 'default' };
      case 'passed':
        return { label: 'Passed', color: 'success' };
      case 'failed':
        return { label: 'Failed', color: 'error' };
      case 'ongoing':
        return { label: 'Ongoing', color: 'warning' };
      default:
        return { label: status, color: 'default' };
    }
  };

  const { label, color } = getStatusProps(status);
  return <Chip label={label} color={color} size="small" />;
}

function SubTopicList({ topics, parentStatus, allTopics, depth = 0 }) {
  const navigate = useNavigate();

  const isAvailable = (topic) => {
    if (depth === 0) {
      return topic.available;
    }
    return parentStatus === 'passed' && topic.available;
  };
  return topics.map((subtopic, index) => {
    
    const available = isAvailable(subtopic);
    return (
    <Box key={subtopic.id}>
      <Box
        sx={{
          display: 'flex',
          alignItems: 'center',
          p: 1.5,
          pl: 2 + depth * 2, // Increase padding for deeper levels
          backgroundColor: index % 2 === 0 ? 'background.default' : 'background.paper',
          borderBottom: '1px solid rgba(0, 0, 0, 0.12)',
          '&:hover': {
            backgroundColor: 'action.hover',
          },
        }}
      >
        <Box sx={{ flex: 1, display: 'flex', alignItems: 'center', gap: 1 }}>
          <Typography variant="body2" noWrap>
            {subtopic.id.replace(/([A-Z])/g, ' $1').trim()}
          </Typography>
          {subtopic.children && subtopic.children.length > 0 && (
            <Chip
              size="small"
              variant="outlined"
              label={`${subtopic.children.length}`}
              sx={{ backgroundColor: 'rgba(0, 0, 0, 0.08)' }}
            />
          )}
          <StatusChip status={getTopicProgress(subtopic)} />
        </Box>
        
                  {/* The button is always a lock icon if parent isn't passed */}
                  <Button
            variant="outlined"
            startIcon={!available ? <Lock /> : 
              subtopic.status === 'passed' ? <Refresh /> : <PlayArrow />
            }
            onClick={() => available && navigate(`/learn/${subtopic.id}`)}
            disabled={!available}
            size="small"
            color={subtopic.status === 'passed' ? 'inherit' : 'primary'}
          >
            {!available ? 'LOCKED' : 
              subtopic.status === 'passed' ? 'Retake' : 'Start'
            }
          </Button>
      </Box>
      {/* Recursively render children if they exist
      {subtopic.children && subtopic.children.length > 0 && (
        <SubTopicList 
          topics={subtopic.children} 
          allTopics={allTopics} 
          depth={depth + 1} 
        />
      )} */}
    </Box>
  )});
}

export function TopicCard({ topic, allTopics }) {
  const navigate = useNavigate();
  const progress = getTopicProgress(topic);
  const actionText = getActionButtonText(topic);
  const available = isTopicAvailable(topic, allTopics);
  
  return (
    <Card elevation={3} sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <CardContent sx={{ flexGrow: 1 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h6" component="div">
            {topic.id.replace(/([A-Z])/g, ' $1').trim()}
          </Typography>
          <StatusChip status={progress} />
        </Box>
      </CardContent>

      <CardActions sx={{ p: 2, pt: 0 }}>
        <Button
          variant="contained"
          startIcon={
            !available ? <Lock /> :
            progress === 'passed' ? <Refresh /> : <PlayArrow />
          }
          onClick={() => navigate(`/learn/${topic.id}`)}
          disabled={!available}
          fullWidth
          size="large"
          color={progress === 'passed' ? 'inherit' : 'primary'}
        >
          {!available ? 'Locked' : actionText}
        </Button>
      </CardActions>

      {topic.children && topic.children.length > 0 && (
        <Box sx={{ px: 2, pb: 2 }}>
          <Typography 
            variant="subtitle1" 
            sx={{ 
              mb: 2,
              fontWeight: 'bold',
              color: 'text.primary'
            }}
          >
            Sub-topics ({topic.children.length})
          </Typography>
          <Paper variant="outlined">
            <SubTopicList 
              topics={topic.children} 
              parentStatus={topic.status}  // Pass the parent topic's status
              allTopics={allTopics} // Pass the complete hierarchy
            />
          </Paper>
        </Box>
      )}
    </Card>
  );
}

function TopicList() {
  const [topics, setTopics] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchTopics = async () => {
      try {
        const response = await axios.get('/api/topics');
        setTopics(response.data);
      } catch (err) {
        setError('Failed to load topics. Please try again later.');
      }
    };

    fetchTopics();
  }, []);

  if (error) {
    return (
      <Typography color="error" align="center">
        {error}
      </Typography>
    );
  }

  return (
    <Box>
    {/* Welcome section */}
    <Grid container spacing={3} sx={{ mb: 4 }}>
      <Grid item xs={12} md={8}>
        <WelcomeCard topicHierarchy={topics} />
      </Grid>
      <Grid item xs={12} md={4}>
        <ProgressGauge topicHierarchy={topics} />
      </Grid>
    </Grid>
      <Grid container spacing={3}>
        {topics.map((topic) => (
          <Grid item xs={12} sm={6} md={4} key={topic.id}>
            <TopicCard topic={topic} />
          </Grid>
        ))}
      </Grid>
    </Box>
  );
}

export default TopicList;