<template>
  <div class="flex flex-col">
    <nav>
      <Button variant="link"><a href="/trip">Go to Trip Planning</a></Button>
      <Button variant="link"><a href="/memories">Go to Memories</a></Button>
    </nav>
    <div class="mt-8 flex flex-col gap-4 container px-8 mx-auto">
      <h1 class="text-4xl font-semibold">Finances</h1>
      <Card>
        <CardHeader>
          <CardTitle>Log an Expense</CardTitle>
        </CardHeader>
        <CardContent>
          <form class="w-full gap-4 flex flex-col" @submit.prevent="logExpense">
            <Input v-model="expense.description" placeholder="Description" required />
            <Input v-model="expense.amount" type="number" placeholder="Amount" required />
            <Button type="submit">Log Expense</Button>
          </form>
        </CardContent>
      </Card>
      <Button class="w-full mt-4" @click="settleUp">Settle Up</Button>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue';
import axios from 'axios';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default {
  name: 'Finances',
  components: {
    Button,
    Input,
    Card,
    CardContent,
    CardHeader,
    CardTitle,
  },
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