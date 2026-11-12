import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  TextField,
  Button,
  Alert,
  Divider,
  Grid,
  Chip,
  Paper,
} from '@mui/material';
import {
  FlashOn as EnergyIcon,
  Login as LoginIcon,
  Person as PersonIcon,
  Build as TechIcon,
  School as StudentIcon,
  AccountBalance as DirectionIcon,
} from '@mui/icons-material';
import { useAuth } from '../context/AuthContext';

export default function Login() {
  const { login, loginAsRole } = useAuth();
  const [email, setEmail] = useState('admin@campus.fr');
  const [password, setPassword] = useState('Admin123!');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    const res = await login(email, password);
    setLoading(false);
    if (!res.success) {
      setError(res.error || 'Erreur lors de la connexion');
    }
  };

  const handleQuickRole = (role, defaultEmail, defaultPwd) => {
    setEmail(defaultEmail);
    setPassword(defaultPwd);
    loginAsRole(role);
  };

  return (
    <Box
      sx={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        bgcolor: '#e8f5e9',
        p: 2,
      }}
    >
      <Card sx={{ maxWidth: 520, width: '100%', borderRadius: 3, boxShadow: '0 8px 24px rgba(0,0,0,0.1)' }}>
        <Box sx={{ bgcolor: '#1b5e20', color: 'white', p: 3, textAlign: 'center' }}>
          <EnergyIcon sx={{ fontSize: 44, color: '#69f0ae' }} />
          <Typography variant="h5" fontWeight="bold">
            EcoSmart Campus
          </Typography>
          <Typography variant="body2" sx={{ color: '#b9f6ca', mt: 0.5 }}>
            Plateforme IoT & IA de pilotage énergétique et environnemental
          </Typography>
          <Chip
            label="Sprint 1 - Authentification JWT & Rôles (RF01 / T03 / T07)"
            size="small"
            sx={{ bgcolor: 'rgba(255,255,255,0.2)', color: 'white', mt: 1.5, fontWeight: 'bold' }}
          />
        </Box>

        <CardContent sx={{ p: 3.5 }}>
          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}

          <form onSubmit={handleSubmit}>
            <TextField
              label="Adresse e-mail"
              fullWidth
              margin="normal"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              size="small"
            />
            <TextField
              label="Mot de passe"
              type="password"
              fullWidth
              margin="normal"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              size="small"
            />

            <Button
              type="submit"
              fullWidth
              variant="contained"
              color="success"
              size="large"
              startIcon={<LoginIcon />}
              disabled={loading}
              sx={{ mt: 2, mb: 1, textTransform: 'none', fontWeight: 'bold', py: 1 }}
            >
              {loading ? 'Connexion en cours...' : 'Se connecter'}
            </Button>
          </form>

          <Divider sx={{ my: 2.5 }}>
            <Typography variant="caption" color="text.secondary">
              OU CONNEXION RAPIDE PAR RÔLE (DÉMONSTRATION)
            </Typography>
          </Divider>

          <Grid container spacing={1.5}>
            <Grid item xs={6}>
              <Paper
                variant="outlined"
                sx={{
                  p: 1.5,
                  cursor: 'pointer',
                  textAlign: 'center',
                  '&:hover': { bgcolor: '#e3f2fd', borderColor: '#1976d2' },
                }}
                onClick={() => handleQuickRole('gestionnaire', 'admin@campus.fr', 'Admin123!')}
              >
                <PersonIcon color="primary" />
                <Typography variant="subtitle2" fontWeight="bold">
                  Gestionnaire
                </Typography>
                <Typography variant="caption" color="text.secondary" display="block">
                  Pilotage global & carte
                </Typography>
              </Paper>
            </Grid>

            <Grid item xs={6}>
              <Paper
                variant="outlined"
                sx={{
                  p: 1.5,
                  cursor: 'pointer',
                  textAlign: 'center',
                  '&:hover': { bgcolor: '#fff3e0', borderColor: '#ed6c02' },
                }}
                onClick={() => handleQuickRole('technicien', 'tech@campus.fr', 'Tech123!')}
              >
                <TechIcon color="warning" />
                <Typography variant="subtitle2" fontWeight="bold">
                  Technicien
                </Typography>
                <Typography variant="caption" color="text.secondary" display="block">
                  Alertes & interventions
                </Typography>
              </Paper>
            </Grid>

            <Grid item xs={6}>
              <Paper
                variant="outlined"
                sx={{
                  p: 1.5,
                  cursor: 'pointer',
                  textAlign: 'center',
                  '&:hover': { bgcolor: '#f3e5f5', borderColor: '#9c27b0' },
                }}
                onClick={() => handleQuickRole('etudiant', 'etudiant@campus.fr', 'Etudiant123!')}
              >
                <StudentIcon color="secondary" />
                <Typography variant="subtitle2" fontWeight="bold">
                  Étudiant
                </Typography>
                <Typography variant="caption" color="text.secondary" display="block">
                  Éco-score & défis
                </Typography>
              </Paper>
            </Grid>

            <Grid item xs={6}>
              <Paper
                variant="outlined"
                sx={{
                  p: 1.5,
                  cursor: 'pointer',
                  textAlign: 'center',
                  '&:hover': { bgcolor: '#ffebee', borderColor: '#d32f2f' },
                }}
                onClick={() => handleQuickRole('direction', 'direction@campus.fr', 'Direction123!')}
              >
                <DirectionIcon color="error" />
                <Typography variant="subtitle2" fontWeight="bold">
                  Direction
                </Typography>
                <Typography variant="caption" color="text.secondary" display="block">
                  Objectifs & bilan IA
                </Typography>
              </Paper>
            </Grid>
          </Grid>
        </CardContent>
      </Card>
    </Box>
  );
}
