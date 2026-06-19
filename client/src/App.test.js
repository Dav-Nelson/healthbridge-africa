import { render, screen } from '@testing-library/react';
import App from './App';

test('renders onboarding modal on initial load', () => {
  render(<App />);
  expect(screen.getByText(/Welcome to HealthBridge/i)).toBeInTheDocument();
});

test('renders the HealthBridge Africa header title behind the modal', () => {
  render(<App />);
  expect(screen.getByText(/HealthBridge Africa/i)).toBeInTheDocument();
});