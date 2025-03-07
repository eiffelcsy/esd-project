<template>
  <div>
    <h1>Memories</h1>
    <form @submit.prevent="addJournalEntry">
      <textarea v-model="journalEntry" placeholder="Write your experience..." required></textarea>
      <button type="submit">Save Entry</button>
    </form>
    <input type="file" @change="uploadMedia" multiple />
  </div>
</template>

<script>
import { ref } from 'vue';
import axios from 'axios';

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