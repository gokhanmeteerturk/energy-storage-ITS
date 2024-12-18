// src/components/Layout.jsx
import { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import {
  Box,
  AppBar,
  Toolbar,
  Typography,
  Drawer,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  IconButton,
  useTheme,
  useMediaQuery,
  Divider,
  CircularProgress,
  Alert
} from '@mui/material';
import {
  Menu as MenuIcon,
  School,
  Storage,
  Logout,
  Science,
  Settings
} from '@mui/icons-material';
import { useTopics } from '../context/TopicContext';
import axios from 'axios';

// Define the width of our navigation drawer
const drawerWidth = 240;

// Helper function to choose appropriate icon for different topic types
const getTopicIcon = (topicId) => {
  const icons = {
    'ChemicalEnergyStorage': <Science />,
    'BatteryEnergyStorage': <Battery90 />,
    'default': <Storage />
  };
  return icons[topicId] || icons.default;
};

function Layout({ children }) {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const [mobileOpen, setMobileOpen] = useState(false);
  const location = useLocation();
  const navigate = useNavigate();
  const { topicHierarchy, setTopicHierarchy } = useTopics();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetch the topic hierarchy when the component mounts
  useEffect(() => {
    const fetchTopicHierarchy = async () => {
      try {
        const response = await axios.get('/api/topics');
        setTopicHierarchy(response.data);
        setLoading(false);
      } catch (err) {
        setError('Failed to load the course structure. Please try refreshing the page.');
        setLoading(false);
      }
    };

    fetchTopicHierarchy();
  }, [setTopicHierarchy]);

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  // Handle navigation to a topic and close mobile drawer if needed
  const handleTopicClick = (topicId) => {
    navigate('/');
    if (isMobile) {
      setMobileOpen(false);
    }
    // Add a slight delay to allow for smooth navigation
    setTimeout(() => {
      const element = document.getElementById(topicId);
      if (element) {
        element.scrollIntoView({ behavior: 'smooth' });
      }
    }, 100);
  };

  // The navigation drawer content
  const drawer = (
    <Box>
      <Toolbar>
        <Typography variant="h6" noWrap sx={{ color: 'primary.main' }}>
          Course Topics
        </Typography>
      </Toolbar>
      <Divider />
      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
          <CircularProgress />
        </Box>
      ) : error ? (
        <Box sx={{ p: 2 }}>
          <Alert severity="error" variant="outlined">
            {error}
          </Alert>
        </Box>
      ) : (
        <List>
          <ListItem 
              button = "true"
              key={1}
              onClick={() => handleTopicClick(2)}
              selected={true}
              sx={{
                '&:hover': {
                  backgroundColor: 'rgba(0, 0, 0, 0.04)',
                },
                '&.Mui-selected': {
                  backgroundColor: 'primary.light',
                  '&:hover': {
                    backgroundColor: 'primary.light',
                  }
                }
              }}
            >
              <ListItemIcon>
                <School />
              </ListItemIcon>
              <ListItemText 
                primary={"Home"}
              />
            </ListItem>
          <ListItem 
              button = "true"
              key={2}
              onClick={() => handleTopicClick(2)}
              selected={false}
              sx={{
                '&:hover': {
                  backgroundColor: 'rgba(0, 0, 0, 0.04)',
                },
                '&.Mui-selected': {
                  backgroundColor: 'primary.light',
                  '&:hover': {
                    backgroundColor: 'primary.light',
                  }
                }
              }}
            >
              <ListItemIcon>
                <Settings />
              </ListItemIcon>
              <ListItemText 
                primary={"Student Profile"}
              />
            </ListItem>
          <ListItem 
              button = "true"
              key={3}
              onClick={() => handleTopicClick(2)}
              selected={false}
              sx={{
                '&:hover': {
                  backgroundColor: 'rgba(0, 0, 0, 0.04)',
                },
                '&.Mui-selected': {
                  backgroundColor: 'primary.light',
                  '&:hover': {
                    backgroundColor: 'primary.light',
                  }
                }
              }}
            >
              <ListItemIcon>
                <Logout />
              </ListItemIcon>
              <ListItemText 
                primary={"Logout"}
              />
            </ListItem>
        </List>
      )}
    </Box>
  );

  return (
    <Box sx={{ display: 'flex' }}>
      {/* Main app bar */}
      <AppBar 
        position="fixed" 
        sx={{ 
          zIndex: (theme) => theme.zIndex.drawer + 1,
          backgroundColor: '#1976d2'
        }}
      >
        <Toolbar>
          <IconButton
            color="inherit"
            aria-label="open drawer"
            edge="start"
            onClick={handleDrawerToggle}
            sx={{ mr: 2, display: { sm: 'none' } }}
          >
            <MenuIcon />
          </IconButton>
          <School sx={{ mr: 2 }} />
          <Typography variant="h6" noWrap component="div" sx={{ flexGrow: 1 }}>
            Energy Storage Systems ITS
          </Typography>
        </Toolbar>
      </AppBar>

      {/* Navigation drawer - mobile version */}
      <Box
        component="nav"
        sx={{ width: { sm: drawerWidth }, flexShrink: { sm: 0 } }}
      >
        <Drawer
          variant="temporary"
          open={mobileOpen}
          onClose={handleDrawerToggle}
          ModalProps={{
            keepMounted: true, // Better mobile performance
          }}
          sx={{
            display: { xs: 'block', sm: 'none' },
            '& .MuiDrawer-paper': { 
              boxSizing: 'border-box', 
              width: drawerWidth,
              backgroundColor: 'background.default'
            },
          }}
        >
          {drawer}
        </Drawer>

        {/* Navigation drawer - desktop version */}
        <Drawer
          variant="permanent"
          sx={{
            display: { xs: 'none', sm: 'block' },
            '& .MuiDrawer-paper': { 
              boxSizing: 'border-box', 
              width: drawerWidth,
              backgroundColor: 'background.default'
            },
          }}
          open
        >
          {drawer}
        </Drawer>
      </Box>

      {/* Main content area */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: 3,
          width: { sm: `calc(100% - ${drawerWidth}px)` },
          mt: 8,
          minHeight: '100vh',
          backgroundColor: 'background.default'
        }}
      >
        {children}
      </Box>
    </Box>
  );
}

export default Layout;