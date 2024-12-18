import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './Profile.css';

const Profile = () => {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const navigate = useNavigate();

    useEffect(() => {
        const fetchProfile = async () => {
            const userid = localStorage.getItem('userid');

            if (!userid) {
                setError('Пользователь не найден. Авторизуйтесь.');
                setLoading(false);
                return navigate('/login');
            }

            try {
                const response = await fetch(`http://127.0.0.1:8000/accounts/api/profile/?userid=${userid}`);

                if (response.ok) {
                    const data = await response.json();
                    setUser(data);
                } else {
                    const errorData = await response.json();
                    setError(errorData.error || 'Ошибка загрузки данных профиля.');
                }
            } catch (err) {
                setError('Ошибка соединения с сервером.');
            } finally {
                setLoading(false);
            }
        };

        fetchProfile();
    }, [navigate]);

    if (loading) {
        return <p>Загрузка...</p>;
    }

    if (error) {
        return <p style={{ color: 'red' }}>{error}</p>;
    }

    return (
        <div className="profile-container">
            <h1>Profile Page</h1>
            {user ? (
                <>
                    <img
                        src={user.profile_photo || 'default-profile.png'}
                        alt="Profile"
                        className="profile-photo-large"
                    />
                    <h1>{user.username}</h1>
                    <p>Email: {user.email}</p>
                </>
            ) : (
                <p>Данные профиля не найдены.</p>
            )}
        </div>
    );
};

export default Profile;
