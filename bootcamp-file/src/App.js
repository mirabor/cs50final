import React from 'react';
import CardEditor from './CardEditor';
import CardViewer from './CardViewer';

class App extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      cards: [
        { front: 'front1', back: 'back1' },
        { front: 'front2', back: 'back2' },
      ],
      editor: true,
      cardIndex: 0,
    };
  }

  addCard = card => {
    if (card.front.trim() !== '' && card.back.trim() !== '') {
      const cards = this.state.cards.slice().concat(card);
      this.setState({ cards });
    }
  };

  deleteCard = index => {
    const cards = this.state.cards.slice();
    cards.splice(index, 1);

    if (cards.length === 0) {
      // Prevent removing all cards
      cards.push({ front: 'Default Front', back: 'Default Back' });
    }

    this.setState(prevState => ({
      cards,
      cardIndex: Math.min(prevState.cardIndex, cards.length - 1),
    }));
  };

  switchMode = () => this.setState({ editor: !this.state.editor });

  goToNextCard = () => {
    this.setState(prevState => ({
      cardIndex: Math.min(prevState.cardIndex + 1, prevState.cards.length - 1),
    }));
  };

  goToPrevCard = () => {
    this.setState(prevState => ({
      cardIndex: Math.max(prevState.cardIndex - 1, 0),
    }));
  };


  render() {
    if (this.state.editor) {
      return (
        <CardEditor
          addCard={this.addCard}
          cards={this.state.cards}
          deleteCard={this.deleteCard}
          switchMode={this.switchMode}
        />
      );
    } else {
      return (
      <CardViewer
      cardIndex={this.state.cardIndex}
      totalCards={this.state.cards.length}
      currentCard={this.state.cards[this.state.cardIndex]}
      switchMode={this.switchMode}
      goToNextCard={this.goToNextCard}
      goToPrevCard={this.goToPrevCard}
    />
      );
    }
  }
}

export default App;
