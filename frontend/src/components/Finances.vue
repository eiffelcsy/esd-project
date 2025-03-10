<template>
  <div>
    <h1>Finances</h1>
    <nav>
      <Button variant="link" to="/trip">Go to Trip Planning</Button>
      <Button variant="link" to="/memories">Go to Memories</Button>
    </nav>
    <br/>
    <form @submit.prevent="logExpense">
      <Input v-model="expense.description" placeholder="Description" required />
      <Input v-model="expense.amount" type="number" placeholder="Amount" required />
      <Button type="submit">Log Expense</Button>
    </form>
    <Button @click="settleUp">Settle Up</Button>
  </div>
</template>

<script>
import { ref } from 'vue';
import axios from 'axios';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';

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