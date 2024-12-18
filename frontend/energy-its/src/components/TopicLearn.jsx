// src/components/TopicLearn.jsx
import { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Paper,
  Typography,
  Box,
  Button,
  List,
  ListItem,
  ListItemText,
  TextField,
    Rating,
  Grid,
  CircularProgress,
  Alert,
  Divider,
  Chip
} from '@mui/material';
import { PlayArrow, Refresh, Lock } from '@mui/icons-material';
import axios from 'axios';
import { useTopics } from '../context/TopicContext';
import { TopicCard } from './TopicList';

import { Star, StarBorder, Send } from '@mui/icons-material';

function ChatMessage({ message, type }) {
    return (
      <Box
        sx={{
          mb: 2,
          p: 2,
          backgroundColor: type === 'user' ? '#e3f2fd' : '#fff',
          borderRadius: 2,
          maxWidth: '85%',
          ml: type === 'user' ? 'auto' : 0,
          boxShadow: '0 1px 2px rgba(0,0,0,0.1)',
        }}
      >
        <Typography variant="body1">{message}</Typography>
      </Box>
    );
  }
  
function RatingRequest({ onSubmit }) {
    const [rating, setRating] = useState(0);
    const [hover, setHover] = useState(-1);
  
    return (
      <Box
        sx={{
          mb: 2,
          p: 2,
          backgroundColor: '#f5f5f5',
          borderRadius: 2,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          gap: 2
        }}
      >
        <Typography variant="body1" sx={{ textAlign: 'center' }}>
          How helpful was this answer? Please rate from 1 to 10
        </Typography>
        <Rating
          value={rating}
          onChange={(event, newValue) => {
            setRating(newValue);
          }}
          onChangeActive={(event, newHover) => {
            setHover(newHover);
          }}
          max={10}
          emptyIcon={<StarBorder sx={{ opacity: 0.55 }} />}
          size="large"
        />
        <Typography variant="body2" sx={{ mt: 1 }}>
          {rating > 0 ? `${rating} out of 10` : 'Click to rate'}
        </Typography>
        <Button 
          variant="contained" 
          onClick={() => onSubmit(rating)}
          disabled={!rating}
          size="small"
        >
          Submit Rating
        </Button>
      </Box>
    );
  }

  
export function ChatPanel({ topicId }) {
    const [messages, setMessages] = useState([]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [waitingForRating, setWaitingForRating] = useState(false);
    const [currentResponse, setCurrentResponse] = useState(null);
    const messagesEndRef = useRef(null);
  
    const scrollToBottom = () => {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };
  
    const handleSend = async (e) => {
      e.preventDefault();
      if (!input.trim() || loading) return;
  
      const question = input.trim();
      setInput('');
      setMessages(prev => [...prev, { text: question, type: 'user' }]);
      setLoading(true);
      setError(null);
  
      try {
        const response = await fetch(`/api/topic/${topicId}/ask`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ question }),
        });
  
        const data = await response.json();
  
        if (!response.ok) {
          throw new Error(data.detail || 'Failed to get answer');
        }
  
        setMessages(prev => [...prev, { text: data.answer, type: 'assistant' }]);
        setCurrentResponse(data);
        setWaitingForRating(true);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };
  
    const handleRatingSubmit = async (rating) => {
      if (!currentResponse) return;
  
      try {
        await fetch(`/api/topic/${topicId}/feedback`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            question: currentResponse.question,
            answer: currentResponse.answer,
            rating: rating,
            shot_list: currentResponse.shot_list
          }),
        });
  
        setMessages(prev => [...prev, {
          text: "Thank you for your feedback! Feel free to ask another question.",
          type: 'system'
        }]);
      } catch (err) {
        // Suppress error as specified
      } finally {
        setWaitingForRating(false);
        setCurrentResponse(null);
      }
    };
  
    return (
      <Paper
        sx={{
          height: '100%',
          display: 'flex',
          flexDirection: 'column',
          backgroundColor: '#f8f9fa',
        }}
      >
        <Box sx={{ p: 2, backgroundColor: 'primary.main', color: 'white' }}>
          <Typography variant="h6">Learning Assistant</Typography>
        </Box>
        
        <Box sx={{ 
          p: 2, 
          flex: 1, 
          overflowY: 'auto',
          display: 'flex',
          flexDirection: 'column'
        }}>
          {messages.map((msg, index) => (
            <ChatMessage 
              key={index} 
              message={msg.text} 
              type={msg.type} 
            />
          ))}
          
          {loading && (
            <Box sx={{ display: 'flex', justifyContent: 'center', p: 2 }}>
              <CircularProgress size={24} />
            </Box>
          )}
  
          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}
  
          {waitingForRating && !loading && (
            <RatingRequest onSubmit={handleRatingSubmit} />
          )}
          
          <div ref={messagesEndRef} />
        </Box>
  
        <Box
          component="form"
          onSubmit={handleSend}
          sx={{
            p: 2,
            borderTop: '1px solid rgba(0, 0, 0, 0.12)',
            backgroundColor: '#fff',
            display: 'flex',
            gap: 1
          }}
        >
          <TextField
            fullWidth
            size="small"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder={waitingForRating ? "Please rate the answer first" : "Ask a question about this topic..."}
            variant="outlined"
            disabled={waitingForRating || loading}
          />
          <Button
            variant="contained"
            onClick={handleSend}
            disabled={waitingForRating || loading || !input.trim()}
            sx={{ minWidth: '56px' }}
          >
            <Send />
          </Button>
        </Box>
      </Paper>
    );
  };
// Main learning page component
function TopicLearn() {
  const { topicId } = useParams();
  const navigate = useNavigate();
  const { findTopicInHierarchy, topicHierarchy } = useTopics();
  const [topicDetail, setTopicDetail] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Get the hierarchical information about the topic
  const hierarchyInfo = findTopicInHierarchy(topicId);

  // Fetch detailed topic information
  useEffect(() => {
    const fetchTopicDetail = async () => {
      try {
        const response = await axios.get(`/api/topic/${topicId}`);
        setTopicDetail(response.data);
        setLoading(false);
      } catch (err) {
        if (err.response?.status === 403) {
          setError('Prerequisites not completed for this topic.');
        } else {
          setError('Failed to load topic content.');
        }
        setLoading(false);
      }
    };

    fetchTopicDetail();
  }, [topicId]);

  const handleStartQuiz = () => {
    navigate(`/quiz/${topicId}`);
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ mt: 2 }}>
        {error}
      </Alert>
    );
  }

  if (!topicDetail || !hierarchyInfo) {
    return (
      <Alert severity="warning" sx={{ mt: 2 }}>
        Topic not found.
      </Alert>
    );
  }

  // Combine hierarchy and detail information
  const combinedTopicInfo = {
    ...topicDetail,
    status: hierarchyInfo.status,
    available: hierarchyInfo.available,
    children: hierarchyInfo.children
  };

  return (
    <Grid container spacing={3} sx={{ height: 'calc(100vh - 100px)' }}>
      <Grid item xs={12} md={8}>
        <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
          <Box sx={{ mb: 3 }}>
            <Typography variant="h4" gutterBottom>
              {combinedTopicInfo.id.replace(/([A-Z])/g, ' $1').trim()}
            </Typography>
            <Chip 
              label={combinedTopicInfo.status.replace(/_/g, ' ').toUpperCase()}
              color={combinedTopicInfo.status === 'passed' ? 'success' : 'default'}
              sx={{ mr: 1 }}
            />
          </Box>
          
          <Typography paragraph>
            {combinedTopicInfo.description}
          </Typography>

          {Object.entries(combinedTopicInfo.properties || {}).length > 0 && (
            <>
              <Divider sx={{ my: 3 }} />
              <Typography variant="h6" gutterBottom>
                Properties
              </Typography>
              <List>
                {Object.entries(combinedTopicInfo.properties).map(([key, values]) => (
                  <ListItem key={key}>
                    <ListItemText
                      primary={key.replace(/([A-Z])/g, ' $1').trim()}
                      secondary={values.join(', ')}
                    />
                  </ListItem>
                ))}
              </List>
            </>
          )}

          <Box sx={{ mt: 4, textAlign: 'center' }}>
            <Button
              variant="contained"
              color="primary"
              size="large"
              onClick={handleStartQuiz}
            >
              Start Quiz
            </Button>
          </Box>
        </Paper>

        {/* Show sub-topics if they exist */}
        {combinedTopicInfo.children && combinedTopicInfo.children.length > 0 && (
          <Box sx={{ mt: 3 }}>
            <Typography variant="h5" gutterBottom>
              Sub-topics ({combinedTopicInfo.children.length})
            </Typography>
            <Grid container spacing={3}>
              {combinedTopicInfo.children.map(childTopic => (
                <Grid item xs={12} md={6} key={childTopic.id}>
                  <TopicCard topic={childTopic} />
                </Grid>
              ))}
            </Grid>
          </Box>
        )}
      </Grid>

      <Grid item xs={12} md={4} sx={{ height: '100%' }}>
        <ChatPanel topicId={topicId} />
      </Grid>
    </Grid>
  );
}

export default TopicLearn;