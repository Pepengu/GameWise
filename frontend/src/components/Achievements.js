// components/Achievements.js
import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

function Achievements() {
    const [achievements, setAchievements] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const navigate = useNavigate();


    useEffect(() => {
        const fetchAchievements = async () => {
            try {
                const user = JSON.parse(localStorage.getItem('user')); // Извлекаем объект user
                const userId = user ? user.id : null; // Проверяем, существует ли user и берём его id

                console.log('Fetched user:', user); // Для отладки
                console.log('Fetched userId:', userId); // Для отладки

                if (!userId) {
                    throw new Error('User not logged in.');
                }

                const response = await axios.get(`/api/user/${userId}/achievements`);
                console.log('Achievements response:', response.data); // Для отладки

                setAchievements(response.data.achievements || []);
            } catch (err) {
                console.error('Error fetching achievements:', err);
                if (err.message === 'User not logged in.') {
                    navigate('/login');
                } else {
                    setError(err.message || 'Failed to load achievements');
                }
            } finally {
                setLoading(false);
            }
        };

        fetchAchievements();
    }, [navigate]);


    if (loading) {
        return <div>Loading achievements...</div>;
    }

    if (error) {
        return <div>Error: {error}</div>;
    }

    return (
        <div>
            <h1>Your Achievements</h1>
            {achievements.length === 0 ? (
                <p>You have no achievements yet.</p>
            ) : (
                <ul>
                    {achievements.map((achievement) => (
                        <li key={achievement.id}>
                            <h3>{achievement.title}</h3>
                            <p>{achievement.description}</p>
                            {achievement.image && (
                                <img src={achievement.image} alt={achievement.title} width="100" />
                            )}
                            <p>Earned on: {new Date(achievement.date_earned).toLocaleDateString()}</p>
                        </li>
                    ))}
                </ul>
            )}
        </div>
    );
}

export default Achievements;
