import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import SelectionPage from './pages/SelectionPage';
import ChatPage from './pages/ChatPage';

export default function App() {
    return (
        <Router>
            <Routes>
                <Route path="/" element={<SelectionPage />} />
                <Route path="/chat" element={<ChatPage />} />
            </Routes>
        </Router>
    );
}
