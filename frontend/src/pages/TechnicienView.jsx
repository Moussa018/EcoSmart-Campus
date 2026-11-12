import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  Button,
  Grid,
  Paper,
  Alert,
} from '@mui/material';
import {
  Build as TechIcon,
  Warning as AlertIcon,
  CheckCircle as OkIcon,
  NotificationsActive as ActiveAlertIcon,
} from '@mui/icons-material';
import { apiClient } from '../mocks/apiMock';

export default function TechnicienView() {
  const [alerts, setAlerts] = useState([]);
  const [acknowledged, setAcknowledged] = useState({});

  useEffect(() => {
    apiClient.getAlerts().then(setAlerts);
  }, []);

  const handleAcquitter = (id) => {
    setAcknowledged((prev) => ({ ...prev, [id]: true }));
  };

  return (
    <Box>
      <Typography variant="h5" fontWeight="bold" gutterBottom>
        Espace Maintenance & Interventions (Sprint 1 - T07)
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
        Traitement des alertes capteurs en temps réel et suivi du matériel de mesure.
      </Typography>

      <Grid container spacing={2.5} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={4}>
          <Paper sx={{ p: 2, display: 'flex', alignItems: 'center', gap: 2 }}>
            <ActiveAlertIcon sx={{ color: '#ed6c02', fontSize: 32 }} />
            <Box>
              <Typography variant="caption" color="text.secondary">
                Alertes non traitées
              </Typography>
              <Typography variant="h6" fontWeight="bold">
                {alerts.filter((a) => a.statut === 'ouverte' && !acknowledged[a.id]).length}
              </Typography>
            </Box>
          </Paper>
        </Grid>

        <Grid item xs={12} sm={4}>
          <Paper sx={{ p: 2, display: 'flex', alignItems: 'center', gap: 2 }}>
            <TechIcon sx={{ color: '#1976d2', fontSize: 32 }} />
            <Box>
              <Typography variant="caption" color="text.secondary">
                Capteurs sous surveillance
              </Typography>
              <Typography variant="h6" fontWeight="bold">
                12 actifs
              </Typography>
            </Box>
          </Paper>
        </Grid>

        <Grid item xs={12} sm={4}>
          <Paper sx={{ p: 2, display: 'flex', alignItems: 'center', gap: 2 }}>
            <OkIcon sx={{ color: '#2e7d32', fontSize: 32 }} />
            <Box>
              <Typography variant="caption" color="text.secondary">
                Temps moyen de prise en charge
              </Typography>
              <Typography variant="h6" fontWeight="bold">
                &lt; 5 min
              </Typography>
            </Box>
          </Paper>
        </Grid>
      </Grid>

      <Card sx={{ borderRadius: 2 }}>
        <CardContent>
          <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
            Journal des alertes de terrain
          </Typography>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>ID</TableCell>
                  <TableCell>Capteur</TableCell>
                  <TableCell>Bâtiment</TableCell>
                  <TableCell>Gravité</TableCell>
                  <TableCell>Message / Anomalie</TableCell>
                  <TableCell>Horodatage</TableCell>
                  <TableCell align="center">Action</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {alerts.map((a) => {
                  const isAck = acknowledged[a.id] || a.statut === 'acquittee';
                  return (
                    <TableRow key={a.id} sx={{ bgcolor: isAck ? '#f5f5f5' : 'inherit' }}>
                      <TableCell>#{a.id}</TableCell>
                      <TableCell fontWeight="medium">{a.capteur_id}</TableCell>
                      <TableCell>{a.batiment_nom}</TableCell>
                      <TableCell>
                        <Chip
                          label={a.gravite.toUpperCase()}
                          size="small"
                          color={a.gravite === 'critique' ? 'error' : 'warning'}
                        />
                      </TableCell>
                      <TableCell>{a.message}</TableCell>
                      <TableCell>{a.ouverte_le}</TableCell>
                      <TableCell align="center">
                        {isAck ? (
                          <Chip label="Pris en charge" size="small" color="success" variant="outlined" />
                        ) : (
                          <Button
                            variant="contained"
                            color="warning"
                            size="small"
                            onClick={() => handleAcquitter(a.id)}
                            sx={{ textTransform: 'none' }}
                          >
                            Acquitter
                          </Button>
                        )}
                      </TableCell>
                    </TableRow>
                  );
                })}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>
    </Box>
  );
}
