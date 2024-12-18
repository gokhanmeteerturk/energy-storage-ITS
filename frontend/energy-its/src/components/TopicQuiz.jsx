
// src/components/TopicQuiz.jsx
import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Paper, Typography, Box, Button, Radio,
  RadioGroup, FormControl, FormControlLabel,
  Alert
} from '@mui/material';
import axios from 'axios';

function TopicQuiz() {
  const { topicId } = useParams();
  const navigate = useNavigate();
  const [quiz, setQuiz] = useState(null);
  const [answers, setAnswers] = useState([]);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchQuiz = async () => {
      try {
        const response = await axios.get(`/api/quiz/${topicId}`);
        setQuiz(response.data);
        setAnswers(new Array(response.data.questions.length).fill(''));
      } catch (err) {
        setError(err.response?.data?.detail || 'Failed to load quiz.');
      }
    };

    fetchQuiz();
  }, [topicId]);

  const handleAnswerChange = (questionIndex, value) => {
    const newAnswers = [...answers];
    newAnswers[questionIndex] = value;
    setAnswers(newAnswers);
  };

  const handleSubmit = async () => {
    try {
      const response = await axios.post(`/api/quiz/${quiz.quiz_id}/submit`, {
        answers: answers.map(selected => ({ selected }))
      });
      setResult(response.data);
    } catch (err) {
      setError('Failed to submit quiz.');
    }
  };

  if (error) {
    return (
      <Typography color="error" align="center">
        {error}
      </Typography>
    );
  }

  if (!quiz) {
    return <Typography>Loading...</Typography>;
  }

  if (result) {
    return (
      <Paper elevation={3} sx={{ p: 3 }}>
        <Typography variant="h5" gutterBottom>
          Quiz Results
        </Typography>
        <Alert severity={result.passed ? "success" : "error"}>
          You {result.passed ? "passed" : "failed"} the quiz with a score of {Math.round(result.score * 100)}%
        </Alert>
        <Box sx={{ mt: 3, textAlign: 'center' }}>
          <Button
            variant="contained"
            onClick={() => navigate('/')}
          >
            Return to Topics
          </Button>
        </Box>
      </Paper>
    );
  }

  return (
    <Paper elevation={3} sx={{ p: 3 }}>
      <Typography variant="h5" gutterBottom>
        Quiz: {topicId}
      </Typography>
      
      {quiz.questions.map((question, index) => (
        <Box key={index} sx={{ mb: 4 }}>
          <Typography variant="h6" gutterBottom>
            Question {index + 1}
          </Typography>
          <Typography paragraph>
            {question.question}
          </Typography>
          <FormControl component="fieldset">
            <RadioGroup
              value={answers[index]}
              onChange={(e) => handleAnswerChange(index, e.target.value)}
            >
              {question.options.map((option, optIndex) => (
                <FormControlLabel
                  key={optIndex}
                  value={option}
                  control={<Radio />}
                  label={option}
                />
              ))}
            </RadioGroup>
          </FormControl>
        </Box>
      ))}

      <Box sx={{ mt: 4, textAlign: 'center' }}>
        <Button
          variant="contained"
          color="primary"
          size="large"
          onClick={handleSubmit}
          disabled={answers.some(a => !a)}
        >
          Submit Quiz
        </Button>
      </Box>
    </Paper>
  );
}

export default TopicQuiz;