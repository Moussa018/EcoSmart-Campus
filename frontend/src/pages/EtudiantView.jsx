import React, { useState } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  Paper,
  LinearProgress,
  Button,
  Chip,
  Avatar,
} from '@mui/material';
import {
  EmojiEvents as TrophyIcon,
  NaturePeople as EcoIcon,
  CheckCircle as DoneIcon,
} from '@mui/icons-material';
import { MOCK_DEFIS, MOCK_BUILDINGS } from '../mocks/apiMock';

export default function EtudiantView() {
  const [joinedDefis, setJoinedDefis] = useState({});

  const handleJoin = (id) => {
    setJoinedDefis((prev) => ({ ...prev, [id]: true }));
  };

  const sortedBuildings = [...MOCK_BUILDINGS].sort((a, b) => b.eco_score - a.eco_score);

  return (
    <Box>
      <Typography variant="h5" fontWeight="bold" gutterBottom>
        Espace Étudiant & Vie Campus (Sprint 1 - T07)
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
        Suivez l'éco-score de votre bâtiment et participez aux défis écologiques du campus.
      </Typography>

      <Grid container spacing={3}>
        {/* Podium Éco-score */}
        <Grid item xs={12} md={5}>
          <Card sx={{ borderRadius: 2 }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                <TrophyIcon sx={{ color: '#fbc02d', fontSize: 28 }} />
                <Typography variant="subtitle1" fontWeight="bold">
                  Classement Éco-score du Campus
                </Typography>
              </Box>

              {sortedBuildings.map((b, index) => (
                <Paper
                  key={b.id}
                  variant="outlined"
                  sx={{
                    p: 1.5,
                    mb: 1.5,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    bgcolor: index === 0 ? '#fffde7' : 'inherit',
                    borderColor: index === 0 ? '#fbc02d' : '#e0e0e0',
                  }}
                >
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
                    <Avatar
                      sx={{
                        width: 28,
                        height: 28,
                        bgcolor: index === 0 ? '#fbc02d' : '#9e9e9e',
                        fontSize: '0.85rem',
                        fontWeight: 'bold',
                      }}
                    >
                      {index + 1}
                    </Avatar>
                    <Box>
                      <Typography variant="body2" fontWeight="bold">
                        {b.nom}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        Zone {b.zone}
                      </Typography>
                    </Box>
                  </Box>
                  <Chip
                    label={`${b.eco_score} pts`}
                    color={index === 0 ? 'success' : 'default'}
                    size="small"
                    sx={{ fontWeight: 'bold' }}
                  />
                </Paper>
              ))}
            </CardContent>
          </Card>
        </Grid>

        {/* Défis en cours */}
        <Grid item xs={12} md={7}>
          <Card sx={{ borderRadius: 2 }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                <EcoIcon sx={{ color: '#2e7d32', fontSize: 28 }} />
                <Typography variant="subtitle1" fontWeight="bold">
                  Défis Éco-citoyens en cours
                </Typography>
              </Box>

              {MOCK_DEFIS.map((d) => {
                const joined = joinedDefis[d.id];
                return (
                  <Paper key={d.id} variant="outlined" sx={{ p: 2, mb: 2, borderRadius: 2 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                      <Box>
                        <Typography variant="subtitle2" fontWeight="bold">
                          {d.titre}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          Cible : {d.batiment} · Fin : {d.fin} · {d.participants} participants
                        </Typography>
                      </Box>
                      <Chip label={`+${d.points} pts`} color="secondary" size="small" />
                    </Box>

                    <Box sx={{ my: 1.5 }}>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                        <Typography variant="caption">Progression collective</Typography>
                        <Typography variant="caption" fontWeight="bold">
                          {d.progression} %
                        </Typography>
                      </Box>
                      <LinearProgress variant="determinate" value={d.progression} color="success" sx={{ height: 8, borderRadius: 4 }} />
                    </Box>

                    {joined ? (
                      <Button variant="outlined" color="success" size="small" startIcon={<DoneIcon />} disabled fullWidth>
                        Participation enregistrée !
                      </Button>
                    ) : (
                      <Button variant="contained" color="success" size="small" onClick={() => handleJoin(d.id)} fullWidth sx={{ textTransform: 'none' }}>
                        Rejoindre le défi
                      </Button>
                    )}
                  </Paper>
                );
              })}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
}
