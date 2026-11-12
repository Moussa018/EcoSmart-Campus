import React from 'react';
import { useAuth } from '../context/AuthContext';
import Layout from '../components/Layout';
import GestionnaireView from './GestionnaireView';
import TechnicienView from './TechnicienView';
import EtudiantView from './EtudiantView';
import DirectionView from './DirectionView';

export default function Dashboard() {
  const { user } = useAuth();
  const role = user?.role || 'gestionnaire';

  const renderRoleView = () => {
    switch (role) {
      case 'technicien':
        return <TechnicienView />;
      case 'etudiant':
        return <EtudiantView />;
      case 'direction':
        return <DirectionView />;
      case 'gestionnaire':
      default:
        return <GestionnaireView />;
    }
  };

  return <Layout>{renderRoleView()}</Layout>;
}
