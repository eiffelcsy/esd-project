<template>
  <div>
    <h1>Memories</h1>
    <nav>
      <Button variant="link" to="/trip">Go to Trip Planning</Button>
      <Button variant="link" to="/finances">Go to Finances</Button>
    </nav>
    <br/>
    <form @submit.prevent="addJournalEntry">
      <Input as="textarea" v-model="journalEntry" placeholder="Write your experience..." required />
      <Button type="submit">Save Entry</Button>
    </form>
    <Input type="file" @change="uploadMedia" multiple />
  </div>
</template>

<script>
import { ref } from 'vue';
import axios from 'axios';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';

export default {
  name: 'Memories',
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