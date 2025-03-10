<template>
  <div class="flex flex-col">
    <nav>
      <Button variant="link"><a href="/trip">Go to Trip Planning</a></Button>
      <Button variant="link"><a href="/finances">Go to Finances</a></Button>
    </nav>
    <div class="mt-8 flex flex-col gap-4 container px-8 mx-auto">
      <h1 class="text-4xl font-semibold">Memories</h1>
      <Card>
        <CardHeader>
          <CardTitle>Journal Entry</CardTitle>
        </CardHeader>
        <CardContent>
          <form class="w-full gap-4 flex flex-col" @submit.prevent="addJournalEntry">
            <Input as="textarea" v-model="journalEntry" placeholder="Write your experience..." required />
            <Button type="submit">Save Entry</Button>
          </form>
        </CardContent>
      </Card>
      <Card class="mt-4">
        <CardHeader>
          <CardTitle>Upload Media</CardTitle>
        </CardHeader>
        <CardContent>
          <Input type="file" @change="uploadMedia" multiple />
        </CardContent>
      </Card>
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
  name: 'Memories',
  components: {
    Button,
    Input,
    Card,
    CardContent,
    CardHeader,
    CardTitle,
  },
  setup() {
    const journalEntry = ref('');

    const addJournalEntry = async () => {
      try {
        await axios.post('/journal', { entry: journalEntry.value });
        alert('Journal entry saved!');
      } catch (error) {
        console.error('Error saving journal entry:', error);
      }
    };

    const uploadMedia = async (event) => {
      const files = event.target.files;
      try {
        for (let file of files) {
          const formData = new FormData();
          formData.append('media', file);
          await axios.post('/media', formData);
        }
        alert('Media uploaded!');
      } catch (error) {
        console.error('Error uploading media:', error);
      }
    };

    return { journalEntry, addJournalEntry, uploadMedia };
  },
};
</script> 