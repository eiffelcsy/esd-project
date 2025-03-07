<template>
  <div>
    <h1>Finances</h1>
    <form @submit.prevent="logExpense">
      <input v-model="expense.description" placeholder="Description" required />
      <input v-model="expense.amount" type="number" placeholder="Amount" required />
      <button type="submit">Log Expense</button>
    </form>
    <button @click="settleUp">Settle Up</button>
  </div>
</template>

<script>
import { ref } from 'vue';
import axios from 'axios';

export default {
  name: 'Finances',
  setup() {
    const expense = ref({ description: '', amount: 0 });

    const logExpense = async () => {
      try {
        await axios.post('/expenses', expense.value);
        alert('Expense logged!');
      } catch (error) {
        console.error('Error logging expense:', error);
      }
    };

    const settleUp = async () => {
      try {
        await axios.post('/expenses/settle-up');
        alert('Expenses settled!');
      } catch (error) {
        console.error('Error settling up expenses:', error);
      }
    };

    return { expense, logExpense, settleUp };
  },
};
</script> 