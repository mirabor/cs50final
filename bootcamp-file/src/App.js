import React from 'react';
import CardEditor from './CardEditor';
import CardViewer from './CardViewer';
import { Switch, Route } from 'react-router-dom';

class App extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      cards: [
        { front: 'front1', back: 'back1' },
        { front: 'front2', back: 'back2' },
      ],
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
    return (
      <Switch>
        <Route exact path="/editor">
          <CardEditor
            addCard={this.addCard}
            cards={this.state.cards}
            deleteCard={this.deleteCard}
          />
        </Route>
        <Route exact path="/viewer">
          <CardViewer cards={this.state.cards} />
        </Route>
      </Switch>
    );
  }
}

export default App;
