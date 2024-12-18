import React from 'react';
import { Link } from 'react-router-dom';
import './Home.css';

const Home = () => {
    return (
        <div className="home-container">
            {/* Верхняя панель навигации */}
            <nav className="navbar">
                <div className="logo"></div>
                <ul className="nav-links">
                    <li><a href="/catalog">Каталог</a></li>
                    <li><a href="/my-courses">Мои курсы</a></li>
                    <li><a href="/leaderboard">Лидерборд</a></li>
                    <li><a href="/about">О проекте</a></li>
                </ul>
                <div className="search-container">
                    <input type="text" placeholder="Placeholder" />
                    <button className="search-button">X</button>
                </div>
                <div className="auth-buttons">
                    <Link to="/login" className="auth-button">Вход</Link>
                    <Link to="/register" className="auth-button">Регистрация</Link>
                </div>
            </nav>

            {/* Основной контент */}
            <div className="content">
                <h1>Добро пожаловать!!</h1>
            </div>
        </div>
    );
};

export default Home;
