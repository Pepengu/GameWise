import React, { useEffect, useState } from 'react';
import Navbar from './Navbar';
import Footer from './Footer';
import { Link } from 'react-router-dom';
import image_anime from './image_anime.jpg';
import './Home.css';

const Home = () => {
    const [displayedText, setDisplayedText] = useState('');
    const fullText = "Добро пожаловать в мир геймифицированного обучения!";

    useEffect(() => {
        let index = 0;
        let timer;

        const addLetter = () => {
            if (index+1 < fullText.length) {
                setDisplayedText(prev => prev + fullText[index]);
                index++;
                timer = setTimeout(addLetter, 70);
            } else {
                clearTimeout(timer);
            }
        };

        addLetter();
        return () => clearTimeout(timer);
    }, []);

    return (
        <div className="home-container">
            <Navbar />
            <div className="home-content">
                <div className="home-text-section">
                    <h1>{displayedText}</h1>
                    <p> Мы понимаем, что традиционные методы обучения могут быть скучными и неэффективными. Поэтому мы разработали уникальную систему, которая позволяет вам учиться в своем темпе, устанавливая собственные цели и получая награды за достижения. Наши курсы охватывают широкий спектр тем — от технологий до искусства — и подходят для всех возрастов. Присоединяйтесь к нашему сообществу и откройте для себя новые горизонты знаний в увлекательной форме!</p>
                    <Link to="/catalog" className="home-button">
                    Перейти к курсам
                    </Link>
                </div>
                <div className="home-image-section">
                    <img src={image_anime} alt="картинка" className="home-profile-image" />
                </div>
            </div>
            <Footer />
        </div>
    );
};

export default Home;
