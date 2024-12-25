import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { UserProvider } from './components/UserContext';
import Home from './components/Home';
import Login from './components/Login';
import Register from './components/Register';
import Profile from './components/Profile';
import About from './components/About';
import Catalog from './components/Catalog';
import MyCourses from './components/MyCourses';
import CourseDetail from './components/CourseDetail';
import CDforMyCourses from './components/CDforMyCourses';
import Leaderboard from './components/Leaderboard';
import CourseForm from './components/CourseForm';
import CourseQuiz from './components/CourseQuiz';
import CreateCourse from './components/CreateCourse';

function App() {
    return (
        <UserProvider>
            <Router>
                <Routes>
                    <Route path="/home" element={<Home />} />
                    <Route path="/login" element={<Login />} />
                    <Route path="/register" element={<Register />} />
                    <Route path="/profile" element={<Profile />} />
                    <Route path="/about" element={<About />} />
                    <Route path="/catalog" element={<Catalog />} />
                    <Route path="/my-courses" element={<MyCourses />} />
                    <Route path="/courses/:id" element={<CourseDetail />} />
                    <Route path="/my-courses/:id" element={<CDforMyCourses />} />
                    <Route path="/courses/:id/add-form" element={<CourseForm />} />
                    <Route path="/courses/:id/quiz" element={<CourseQuiz />} />
                    <Route path="/leaderboard" element={<Leaderboard />} />
                    <Route path="/create-course" element={<CreateCourse />} />
                </Routes>
            </Router>
        </UserProvider>
    );
}

export default App;
