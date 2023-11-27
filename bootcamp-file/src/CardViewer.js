import React from 'react';
import './CardViewer.css';

class CardViewer extends React.Component {
  state = {
    isFrontVisible: true,
  };

  handleCardClick = () => {
    this.setState((prevState) => ({ isFrontVisible: !prevState.isFrontVisible }));
  };

  render() {
    const {
      cardIndex,
      totalCards,
      currentCard,
      switchMode,
      goToNextCard,
      goToPrevCard,
    } = this.props;

    const isNextDisabled = cardIndex === totalCards - 1;
    const isPrevDisabled = cardIndex === 0;

    return (
      <div>
        <h2>Card Viewer</h2>
        <hr />
        <div>
          <div>{`Card ${cardIndex + 1}/${totalCards}`}</div>
          <div>
            <button onClick={goToPrevCard} disabled={isPrevDisabled}>
              Previous Card
            </button>
            <button onClick={goToNextCard} disabled={isNextDisabled}>
              Next Card
            </button>
          </div>
          <div>
            <button onClick={switchMode}>Go to card editor</button>
          </div>
        </div>
        <hr />
        <div className={`flashcard ${this.state.isFrontVisible ? 'front' : 'back'}`} onClick={this.handleCardClick}>
          <div className="flashcard-content">
            <div className="text">
              {this.state.isFrontVisible ? (
                <React.Fragment>
                  <div className="front-content">
                    <h3 className="flashcard-title">Front card</h3>
                    <p>{currentCard.front}</p>
                  </div>
                </React.Fragment>
              ) : (
                <React.Fragment>
                  <div className="back-content">
                    <h3 className="flashcard-title">Back card</h3>
                    <p>{currentCard.back}</p>
                  </div>
                </React.Fragment>
              )}
            </div>
          </div>
        </div>
      </div>
    );
  }
}

export default CardViewer;
