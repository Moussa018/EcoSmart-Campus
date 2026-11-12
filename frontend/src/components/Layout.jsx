import React, { useState } from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  IconButton,
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Box,
  Chip,
  Button,
  Avatar,
  Menu,
  MenuItem,
  Divider,
} from '@mui/material';
import {
  Menu as MenuIcon,
  Dashboard as DashboardIcon,
  FlashOn as EnergyIcon,
  Warning as AlertIcon,
  SmartToy as AssistantIcon,
  Build as TechIcon,
  EmojiEvents as TrophyIcon,
  Assessment as DirectionIcon,
  Map as MapIcon,
  Logout as LogoutIcon,
  AccountCircle as AccountIcon,
  SwapHoriz as SwitchRoleIcon,
} from '@mui/icons-material';
import { useAuth } from '../context/AuthContext';

const DRAWER_WIDTH = 260;

const ROLE_CONFIGS = {
  gestionnaire: {
    label: 'Gestionnaire Campus',
    color: 'primary',
    menuItems: [
      { text: 'Tableau de bord', icon: <DashboardIcon /> },
      { text: 'Carte du Campus', icon: <MapIcon /> },
      { text: 'Module Énergie', icon: <EnergyIcon /> },
      { text: 'Alertes & Seuils', icon: <AlertIcon /> },
      { text: 'Assistant EcoSmart', icon: <AssistantIcon /> },
    ],
  },
  technicien: {
    label: 'Technicien Maintenance',
    color: 'warning',
    menuItems: [
      { text: 'Alertes Actives', icon: <AlertIcon /> },
      { text: "Tickets d'intervention", icon: <TechIcon /> },
      { text: 'État des capteurs', icon: <EnergyIcon /> },
    ],
  },
  etudiant: {
    label: 'Étudiant / Résident',
    color: 'secondary',
    menuItems: [
      { text: 'Éco-score Bâtiment', icon: <TrophyIcon /> },
      { text: 'Classement du Campus', icon: <DashboardIcon /> },
      { text: 'Défis Éco-citoyens', icon: <TrophyIcon /> },
    ],
  },
  direction: {
    label: 'Direction Établissement',
    color: 'error',
    menuItems: [
      { text: 'Vue Stratégique', icon: <DirectionIcon /> },
      { text: 'Objectifs & Prévisions', icon: <DashboardIcon /> },
      { text: 'Bilan & Assistant', icon: <AssistantIcon /> },
    ],
  },
};

export default function Layout({ children }) {
  const { user, logout, loginAsRole } = useAuth();
  const [mobileOpen, setMobileOpen] = useState(false);
  const [roleAnchorEl, setRoleAnchorEl] = useState(null);

  const currentRole = user?.role || 'gestionnaire';
  const roleConfig = ROLE_CONFIGS[currentRole] || ROLE_CONFIGS.gestionnaire;

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  const handleOpenRoleMenu = (event) => {
    setRoleAnchorEl(event.currentTarget);
  };

  const handleCloseRoleMenu = (newRole) => {
    setRoleAnchorEl(null);
    if (newRole && typeof newRole === 'string') {
      loginAsRole(newRole);
    }
  };

  const drawerContent = (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Box sx={{ p: 2, display: 'flex', alignItems: 'center', gap: 1.5, bgcolor: '#1b5e20', color: 'white' }}>
        <EnergyIcon sx={{ fontSize: 32, color: '#69f0ae' }} />
        <Box>
          <Typography variant="h6" fontWeight="bold" sx={{ lineHeight: 1.1 }}>
            EcoSmart
          </Typography>
          <Typography variant="caption" sx={{ color: '#b9f6ca', letterSpacing: 1 }}>
            CAMPUS IOT & IA
          </Typography>
        </Box>
      </Box>

      <Box sx={{ p: 2, borderBottom: '1px solid #e0e0e0', bgcolor: '#f9fbe7' }}>
        <Typography variant="caption" color="text.secondary">
          PROFIL ACTIF (Sprint 1 - T07)
        </Typography>
        <Box sx={{ mt: 0.5, display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Chip
            label={roleConfig.label}
            color={roleConfig.color}
            size="small"
            sx={{ fontWeight: 'bold' }}
          />
        </Box>
        <Typography variant="body2" sx={{ mt: 1, fontWeight: 'medium' }}>
          {user?.nom}
        </Typography>
        <Typography variant="caption" color="text.secondary">
          {user?.email}
        </Typography>
      </Box>

      <List sx={{ flexGrow: 1, pt: 1 }}>
        {roleConfig.menuItems.map((item, index) => (
          <ListItem key={item.text} disablePadding>
            <ListItemButton selected={index === 0}>
              <ListItemIcon sx={{ color: index === 0 ? 'primary.main' : 'inherit' }}>
                {item.icon}
              </ListItemIcon>
              <ListItemText
                primary={item.text}
                primaryTypographyProps={{
                  fontWeight: index === 0 ? 'bold' : 'normal',
                  fontSize: '0.9rem',
                }}
              />
            </ListItemButton>
          </ListItem>
        ))}
      </List>

      <Divider />
      <Box sx={{ p: 2 }}>
        <Button
          fullWidth
          variant="outlined"
          color="inherit"
          startIcon={<LogoutIcon />}
          onClick={logout}
          size="small"
        >
          Déconnexion
        </Button>
      </Box>
    </Box>
  );

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh', bgcolor: '#f4f6f8' }}>
      <AppBar
        position="fixed"
        sx={{
          width: { sm: `calc(100% - ${DRAWER_WIDTH}px)` },
          ml: { sm: `${DRAWER_WIDTH}px` },
          bgcolor: 'white',
          color: '#1a1a1a',
          boxShadow: '0 1px 3px rgba(0,0,0,0.08)',
        }}
      >
        <Toolbar sx={{ justifyContent: 'space-between' }}>
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <IconButton
              color="inherit"
              edge="start"
              onClick={handleDrawerToggle}
              sx={{ mr: 2, display: { sm: 'none' } }}
            >
              <MenuIcon />
            </IconButton>
            <Typography variant="subtitle1" fontWeight="bold">
              {roleConfig.label} · Vue opérationnelle
            </Typography>
          </Box>

          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
            {/* Sélecteur rapide de rôle pour la soutenance / démo */}
            <Button
              variant="outlined"
              size="small"
              startIcon={<SwitchRoleIcon />}
              onClick={handleOpenRoleMenu}
              sx={{ textTransform: 'none', borderRadius: 2 }}
            >
              Changer de rôle
            </Button>
            <Menu
              anchorEl={roleAnchorEl}
              open={Boolean(roleAnchorEl)}
              onClose={() => handleCloseRoleMenu(null)}
            >
              <MenuItem onClick={() => handleCloseRoleMenu('gestionnaire')}>
                👔 Gestionnaire Campus (admin@campus.fr)
              </MenuItem>
              <MenuItem onClick={() => handleCloseRoleMenu('technicien')}>
                🔧 Technicien Maintenance (tech@campus.fr)
              </MenuItem>
              <MenuItem onClick={() => handleCloseRoleMenu('etudiant')}>
                🎓 Étudiant / Résident (etudiant@campus.fr)
              </MenuItem>
              <MenuItem onClick={() => handleCloseRoleMenu('direction')}>
                🏛️ Direction Établissement (direction@campus.fr)
              </MenuItem>
            </Menu>

            <Chip
              label={user?.role?.toUpperCase()}
              color={roleConfig.color}
              size="small"
              sx={{ fontWeight: 'bold' }}
            />
            <Avatar sx={{ width: 32, height: 32, bgcolor: '#2e7d32' }}>
              {user?.nom?.charAt(0) || 'U'}
            </Avatar>
          </Box>
        </Toolbar>
      </AppBar>

      <Box
        component="nav"
        sx={{ width: { sm: DRAWER_WIDTH }, flexShrink: { sm: 0 } }}
      >
        <Drawer
          variant="temporary"
          open={mobileOpen}
          onClose={handleDrawerToggle}
          ModalProps={{ keepMounted: true }}
          sx={{
            display: { xs: 'block', sm: 'none' },
            '& .MuiDrawer-paper': { boxSizing: 'border-box', width: DRAWER_WIDTH },
          }}
        >
          {drawerContent}
        </Drawer>
        <Drawer
          variant="permanent"
          sx={{
            display: { xs: 'none', sm: 'block' },
            '& .MuiDrawer-paper': { boxSizing: 'border-box', width: DRAWER_WIDTH },
          }}
          open
        >
          {drawerContent}
        </Drawer>
      </Box>

      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: 3,
          width: { sm: `calc(100% - ${DRAWER_WIDTH}px)` },
          mt: 8,
        }}
      >
        {children}
      </Box>
    </Box>
  );
}
