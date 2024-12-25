import React, { useEffect, useState } from 'react';
import axios from 'axios';
import Navbar from './Navbar';
import Footer from './Footer';
import './Leaderboard.css';

const Leaderboard = () => {
  const [leaderboardData, setLeaderboardData] = useState([]);

  useEffect(() => {
    axios
      .get('http://127.0.0.1:8000/accounts/api/courses/users')
      .then((response) => {

        const sortedData = response.data.user_correct_answers.sort(
          (a, b) => b.correct_answers - a.correct_answers
        );
        setLeaderboardData(sortedData);
      })
      .catch((error) => console.error('Error fetching leaderboard data:', error));
  }, []);

  return (
    <div className="leaderboard">
      <Navbar />
      <div className='leaderboard-content'>
        <h1>Лидерборд</h1>
        <table>
          <thead>
            <tr>
              <th>Место</th>
              <th>Пользователь</th>
              <th>Количество очков</th>
            </tr>
          </thead>
          <tbody>
            {leaderboardData.map((user, index) => (
              <tr key={user.user_id}>
                <td>{index + 1}</td>
                <td>{user.username}</td>
                <td>{user.correct_answers}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <Footer />
    </div>
);

};

export default Leaderboard;
