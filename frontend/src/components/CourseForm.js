import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import './CourseForm.css';

const CourseForm = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [questions, setQuestions] = useState([
    { text: '', options: [{ text: '', is_correct: false }] },
  ]);

  const addQuestion = () => {
    setQuestions([...questions, { text: '', options: [{ text: '', is_correct: false }] }]);
  };

  const addOption = (index) => {
    const newQuestions = [...questions];
    newQuestions[index].options.push({ text: '', is_correct: false });
    setQuestions(newQuestions);
  };

  const handleQuestionChange = (index, text) => {
    const newQuestions = [...questions];
    newQuestions[index].text = text;
    setQuestions(newQuestions);
  };

  const handleOptionChange = (qIndex, oIndex, text, isCorrect) => {
    const newQuestions = [...questions];
    newQuestions[qIndex].options[oIndex] = { text, is_correct: isCorrect };
    setQuestions(newQuestions);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    const requestData = {
      questions: questions.map(question => ({
        text: question.text,
        options: question.options.map(option => ({
          text: option.text,
          is_correct: option.is_correct
        }))
      }))
    };

    try {
      const response = await fetch(`http://127.0.0.1:8000/accounts/api/courses/${id}/add-form/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestData),
      });

      const data = await response.json();
      alert(data.message || 'Ошибка при добавлении формы');
    } catch (error) {
      alert('Ошибка при отправке формы');
      console.error(error);
    }
  };

  if (!id) {
    return <div>Не указан идентификатор курса</div>;
  }

  return (
    <div className="course-form">
      <h2>Добавить форму для курса</h2>
      <form onSubmit={handleSubmit}>
        {questions.map((question, qIndex) => (
          <div className="form-group" key={qIndex}>
            <label>Вопрос {qIndex + 1}</label>
            <input
              type="text"
              value={question.text}
              onChange={(e) => handleQuestionChange(qIndex, e.target.value)}
              placeholder="Введите текст вопроса"
              required
            />
            {question.options.map((option, oIndex) => (
              <div className="option-group" key={oIndex}>
                <input
                  type="text"
                  value={option.text}
                  onChange={(e) =>
                    handleOptionChange(qIndex, oIndex, e.target.value, option.is_correct)
                  }
                  placeholder="Введите вариант ответа"
                  required
                />
                <label>
                  <input
                    type="checkbox"
                    checked={option.is_correct}
                    onChange={(e) =>
                      handleOptionChange(qIndex, oIndex, option.text, e.target.checked)
                    }
                  />
                  Правильный
                </label>
              </div>
            ))}
            <button type="button" className="add-option-button" onClick={() => addOption(qIndex)}>
              Добавить вариант
            </button>
          </div>
        ))}
        <button type="button" className="add-question-button" onClick={addQuestion}>
          Добавить вопрос
        </button>
        <button type="submit" className="submit-button">Сохранить форму</button>
      </form>
      <button className="back-button" onClick={() => navigate(`/my-courses/${id}`)}>Вернуться к курсу</button>
    </div>
  );
};

export default CourseForm;
