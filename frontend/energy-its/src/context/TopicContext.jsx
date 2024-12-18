// src/context/TopicContext.jsx
import { createContext, useContext, useState } from 'react';

const TopicContext = createContext();

export function TopicProvider({ children }) {
  const [topicHierarchy, setTopicHierarchy] = useState([]);

  const findTopicInHierarchy = (topicId, topics = topicHierarchy) => {
    for (const topic of topics) {
      if (topic.id === topicId) {
        return topic;
      }
      if (topic.children) {
        const found = findTopicInHierarchy(topicId, topic.children);
        if (found) return found;
      }
    }
    return null;
  };

  return (
    <TopicContext.Provider value={{ topicHierarchy, setTopicHierarchy, findTopicInHierarchy }}>
      {children}
    </TopicContext.Provider>
  );
}

export function useTopics() {
  const context = useContext(TopicContext);
  if (!context) {
    throw new Error('useTopics must be used within a TopicProvider');
  }
  return context;
}