// src/App.jsx
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material';
import CssBaseline from '@mui/material/CssBaseline';
import TopicList from './components/TopicList';
import TopicLearn from './components/TopicLearn';
import TopicQuiz from './components/TopicQuiz';
import Layout from './components/Layout';
import './App.css'
import { TopicProvider } from './context/TopicContext';
const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <TopicProvider>
        <Router>
          <Layout>
            <Routes>
              <Route path="/" element={<TopicList />} />
              <Route path="/learn/:topicId" element={<TopicLearn />} />
              <Route path="/quiz/:topicId" element={<TopicQuiz />} />
            </Routes>
          </Layout>
        </Router>
      </TopicProvider>
    </ThemeProvider>
  );
}

export default App;