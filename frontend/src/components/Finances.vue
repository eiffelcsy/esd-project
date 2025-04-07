<template>
  <div class="flex flex-col container mx-auto">
    <nav class="flex gap-4 p-4 justify-between items-center mb-4">
      <Button variant="link">
        <router-link :to="{ name: 'trip-planning', params: { tripId: route.params.tripId }}">Planning</router-link>
      </Button>
      <Button variant="secondary">
        <ArrowLeft class="h-4 w-4 mr-1" />
        <router-link to="/groups">Back to Groups</router-link>
      </Button>
    </nav>
    <div class="mt-8 flex flex-col gap-4 container px-8 mx-auto">
      <h1 class="text-4xl font-semibold">Trip Finances</h1>

      <!-- Trip Summary -->
      <Card>
        <CardHeader>
          <CardTitle>Trip Summary</CardTitle>
        </CardHeader>
        <CardContent>
          <div class="space-y-2">
            <div class="flex justify-between">
              <span class="font-semibold">Destination:</span>
              <span>{{ trip.destination }}</span>
            </div>
            <div class="flex justify-between">
              <span class="font-semibold">Local Currency:</span>
              <span>{{ trip.localCurrency }}</span>
            </div>
            <div class="flex justify-between items-center">
              <span class="font-semibold">Display Currency:</span>
              <Select v-model="displayCurrency" @update:modelValue="updateDisplayCurrency">
                <SelectTrigger class="w-[180px]">
                  <SelectValue :placeholder="displayCurrency" />
                </SelectTrigger>
                <SelectContent>
                  <SelectGroup>
                    <SelectLabel>Common Currencies</SelectLabel>
                    <SelectItem value="USD">USD - US Dollar</SelectItem>
                    <SelectItem value="EUR">EUR - Euro</SelectItem>
                    <SelectItem value="JPY">JPY - Japanese Yen</SelectItem>
                    <SelectItem value="GBP">GBP - British Pound</SelectItem>
                    <SelectItem value="AUD">AUD - Australian Dollar</SelectItem>
                    <SelectItem value="CAD">CAD - Canadian Dollar</SelectItem>
                    <SelectItem value="CHF">CHF - Swiss Franc</SelectItem>
                    <SelectItem value="CNY">CNY - Chinese Yuan</SelectItem>
                    <SelectItem value="HKD">HKD - Hong Kong Dollar</SelectItem>
                    <SelectItem value="NZD">NZD - New Zealand Dollar</SelectItem>
                  </SelectGroup>
                  <SelectGroup>
                    <SelectLabel>Asian Currencies</SelectLabel>
                    <SelectItem value="SGD">SGD - Singapore Dollar</SelectItem>
                    <SelectItem value="KRW">KRW - South Korean Won</SelectItem>
                    <SelectItem value="TWD">TWD - Taiwan Dollar</SelectItem>
                    <SelectItem value="THB">THB - Thai Baht</SelectItem>
                    <SelectItem value="MYR">MYR - Malaysian Ringgit</SelectItem>
                    <SelectItem value="IDR">IDR - Indonesian Rupiah</SelectItem>
                    <SelectItem value="PHP">PHP - Philippine Peso</SelectItem>
                    <SelectItem value="VND">VND - Vietnamese Dong</SelectItem>
                  </SelectGroup>
                  <SelectGroup>
                    <SelectLabel>Other Major Currencies</SelectLabel>
                    <SelectItem value="INR">INR - Indian Rupee</SelectItem>
                    <SelectItem value="BRL">BRL - Brazilian Real</SelectItem>
                    <SelectItem value="RUB">RUB - Russian Ruble</SelectItem>
                    <SelectItem value="ZAR">ZAR - South African Rand</SelectItem>
                    <SelectItem value="MXN">MXN - Mexican Peso</SelectItem>
                  </SelectGroup>
                </SelectContent>
              </Select>
            </div>
            <div class="flex justify-between">
              <span class="font-semibold">Exchange Rate:</span>
              <span>1 {{ trip.localCurrency }} = {{ trip.exchangeRate }} {{ displayCurrency }}</span>
            </div>
          </div>
        </CardContent>
      </Card>

      <!-- Add Expense -->
      <Card>
        <CardHeader>
          <CardTitle>Add Expense</CardTitle>
        </CardHeader>
        <CardContent>
          <form @submit.prevent="addExpense" class="space-y-4">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div class="space-y-2">
                <Label for="amount">Amount</Label>
                <div class="flex gap-2">
                  <Input
                    id="amount"
                    v-model="newExpense.amount"
                    type="number"
                    step="0.01"
                    required
                  />
                  <Select v-model="newExpense.currency">
                    <SelectTrigger>
                      <SelectValue :placeholder="trip.localCurrency" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem :value="trip.localCurrency">{{ trip.localCurrency }}</SelectItem>
                      <SelectItem :value="displayCurrency">{{ displayCurrency }}</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
              <div class="space-y-2">
                <Label for="description">Description</Label>
                <Input
                  id="description"
                  v-model="newExpense.description"
                  required
                />
              </div>
            </div>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div class="space-y-2">
                <Label for="payer">Paid by</Label>
                <Select v-model="newExpense.user_id">
                  <SelectTrigger>
                    <SelectValue placeholder="Select payer" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem v-for="member in groupMembers" :key="member.id" :value="member.id">
                      {{ member.name }}
                    </SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div class="space-y-2">
                <Label for="payee">Paid for</Label>
                <Select v-model="newExpense.payees" multiple>
                  <SelectTrigger>
                    <SelectValue placeholder="Select payees" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">Everyone (Split equally)</SelectItem>
                    <SelectItem v-for="member in groupMembers" :key="member.id" :value="member.id">
                      {{ member.name }}
                    </SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
            <div class="space-y-2">
              <Label for="category">Category</Label>
              <Select v-model="newExpense.category">
                <SelectTrigger>
                  <SelectValue placeholder="Select category" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="food">Food & Drinks</SelectItem>
                  <SelectItem value="transportation">Transportation</SelectItem>
                  <SelectItem value="accommodation">Accommodation</SelectItem>
                  <SelectItem value="activities">Activities</SelectItem>
                  <SelectItem value="shopping">Shopping</SelectItem>
                  <SelectItem value="other">Other</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div class="flex justify-end">
              <Button type="submit">Add Expense</Button>
            </div>
          </form>
        </CardContent>
      </Card>

      <!-- Expenses List -->
      <Card>
        <CardHeader>
          <CardTitle>Expenses</CardTitle>
          <CardDescription>All expenses for this trip</CardDescription>
        </CardHeader>
        <CardContent>
          <div v-if="expenses.length" class="space-y-4">
            <div v-for="expense in expenses" :key="expense.id" class="border rounded-lg p-4">
              <div class="flex justify-between items-start">
                <div>
                  <h3 class="font-semibold">{{ expense.description }}</h3>
                  <p class="text-sm text-gray-600">{{ expense.category }}</p>
                </div>
                <div class="text-right">
                  <p class="font-medium">{{ expense.amount }} {{ expense.currency }}</p>
                  <p class="text-sm text-gray-500">
                    {{ expense.convertedAmount }} {{ expense.displayCurrency }}
                  </p>
                </div>
              </div>
              <div class="mt-2 flex justify-between items-center text-sm text-gray-500">
                <div>
                  Added by User {{ expense.addedBy }} on {{ formatDate(expense.date) }}
                </div>
                <div v-if="expense.payee">
                  <span class="font-medium">Paid for:</span> {{ expense.payee }}
                </div>
              </div>
            </div>
          </div>
          <div v-else class="text-center py-4 text-gray-500">
            No expenses added yet.
          </div>
        </CardContent>
      </Card>

      <!-- Settlement Status -->
      <Card>
        <CardHeader>
          <CardTitle>Settlement Status</CardTitle>
          <CardDescription>Track who has finished adding expenses</CardDescription>
        </CardHeader>
        <CardContent>
          <div class="space-y-4">
            <div v-for="member in groupMembers" :key="member.id" class="flex items-center justify-between">
              <div class="flex items-center gap-2">
                <div class="w-2 h-2 rounded-full" :class="member.ready ? 'bg-green-500' : 'bg-yellow-500'"></div>
                <span>{{ member.name }}</span>
              </div>
              <Button
                v-if="!member.ready && member.id === currentUserId"
                size="sm"
                @click="markAsReady"
              >
                Mark as Ready
              </Button>
            </div>

            <div v-if="allMembersReady" class="mt-4 p-4 bg-green-50 rounded-lg">
              <h3 class="font-semibold text-green-800">All members are ready!</h3>
              <p class="text-sm text-green-700 mt-1">
                Final calculations have been performed. Check your email for settlement details.
              </p>
              <div class="mt-4">
                <Button @click="viewSettlementDetails" variant="outline">
                  View Settlement Details
                </Button>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>

    <!-- Settlement Details Modal -->
    <Dialog v-model:open="showSettlementModal">
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Settlement Details</DialogTitle>
          <DialogDescription>
            Here's how much each person needs to pay
          </DialogDescription>
        </DialogHeader>
        <div class="space-y-4">
          <div v-if="settlementDetails.length === 0" class="text-center py-4 text-gray-500">
            No settlements needed. Everyone is even!
          </div>
          <div v-for="settlement in settlementDetails" :key="`${settlement.from}-${settlement.to}`" class="border rounded-lg p-4">
            <div class="flex justify-between items-center">
              <div>
                <p class="font-medium">{{ settlement.from_name }}</p>
                <p class="text-sm text-gray-600">pays to {{ settlement.to_name }}</p>
              </div>
              <p class="font-semibold">{{ settlement.amount }} {{ settlement.currency }}</p>
            </div>
          </div>
        </div>
      </DialogContent>
    </Dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { useRoute } from "vue-router";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from "@/components/ui/dialog";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue, SelectGroup, SelectLabel } from "@/components/ui/select";
import { PencilIcon, TrashIcon, RefreshCw, ArrowLeft } from "lucide-vue-next";

const route = useRoute();
const trip = ref({});
const expenses = ref([]);
const groupMembers = ref([]);
const currentUserId = ref(null);
const showSettlementModal = ref(false);
const settlementDetails = ref([]);
const settlementCurrency = ref('SGD');
const displayCurrency = ref('SGD');

const newExpense = ref({
  amount: "",
  currency: "",
  description: "",
  category: "",
  user_id: "",
  payees: ["all"],
});

const allMembersReady = computed(() => {
  return groupMembers.value.every(member => member.ready);
});

const fetchTripDetails = async () => {
  try {
    // First get trip details from trip-management service
    const tripResponse = await fetch(`http://localhost:5005/api/trips/${route.params.tripId}`);
    if (!tripResponse.ok) {
      throw new Error(`HTTP error! Status: ${tripResponse.status}`);
    }
    const tripData = await tripResponse.json();
    
    const currencyMap = {
      'Tokyo': 'JPY',
      'Seoul': 'KRW',
      'Bangkok': 'THB',
      'Singapore': 'SGD',
      'Kuala Lumpur': 'MYR',
      'Jakarta': 'IDR',
      'Manila': 'PHP',
      'Hong Kong': 'HKD',
      'Beijing': 'CNY',
      'Shanghai': 'CNY',
      'Osaka': 'JPY',
      'Taipei': 'TWD',
      'Ho Chi Minh City': 'VND',
      'Hanoi': 'VND',
      'Bali': 'IDR'
    };
    
    const localCurrency = currencyMap[tripData.city] || 'USD';
    
    // Get exchange rate from expense-management service
    try {
      console.log(`Fetching exchange rate for ${localCurrency} to USD`);
      const rateResponse = await fetch(`http://localhost:5007/api/expenses/convert/${localCurrency}/USD/1.0`, {
        method: 'GET',
        headers: {
          'Accept': 'application/json'
        }
      });
      console.log('Rate response status:', rateResponse.status);
      
      let exchangeRate = 1;
      if (rateResponse.ok) {
        const rateData = await rateResponse.json();
        console.log('Rate data received:', rateData);
        
        if (rateData && typeof rateData === 'object') {
          if ('rate' in rateData) {
            exchangeRate = rateData.rate;
          } else if ('converted_amount' in rateData) {
            exchangeRate = rateData.converted_amount;
          } else if ('error' in rateData) {
            console.warn('Exchange rate error:', rateData.error);
            // Use fallback rate of 1.0
          }
        }
      } else {
        console.error('Failed to fetch exchange rate:', await rateResponse.text());
      }
      
      // Update trip data with currency information
      trip.value = {
        ...tripData,
        destination: tripData.city,
        localCurrency,
        exchangeRate: Number(exchangeRate).toFixed(4)
      };
      
      // Set default currency for new expenses
      newExpense.value.currency = localCurrency;
    } catch (error) {
      console.error('Error fetching exchange rate:', error);
      // Set default values in case of error
      trip.value = {
        ...tripData,
        destination: tripData.city,
        localCurrency,
        exchangeRate: '1.0000'
      };
      newExpense.value.currency = localCurrency;
    }
    
    await fetchExpenses();
    await fetchGroupMembers();
  } catch (error) {
    console.error("Error fetching trip details:", error);
  }
};

const fetchExpenses = async () => {
  try {
    const response = await fetch(`http://localhost:5007/api/expenses/${route.params.tripId}`);
    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }
    const data = await response.json();
    
    expenses.value = await Promise.all(data.expenses.map(async expense => {
      // Convert amount to display currency if it's different from the base currency
      let convertedAmount = expense.amount;
      if (expense.base_currency !== displayCurrency.value) {
        try {
          const conversionResponse = await fetch(
            `http://localhost:5007/api/expenses/convert/${expense.base_currency}/${displayCurrency.value}/${expense.amount.toFixed(2)}`,
            {
              method: 'GET',
              headers: {
                'Accept': 'application/json'
              }
            }
          );
          if (conversionResponse.ok) {
            const conversionData = await conversionResponse.json();
            convertedAmount = conversionData.converted_amount || conversionData.rate * expense.amount;
          }
        } catch (error) {
          console.error("Error converting amount:", error);
          // Fallback to using the stored exchange rate
          convertedAmount = expense.amount * Number(trip.value.exchangeRate);
        }
      }

      // Find the payer's name from group members
      const payer = groupMembers.value.find(m => String(m.id) === String(expense.user_id));
      const payerName = payer ? payer.name : `User ${expense.user_id}`;

      // Process payees information
      let payeeNames = 'Everyone';
      
      if (expense.payees && Array.isArray(expense.payees) && !expense.payees.includes("all")) {
        const payeesList = expense.payees.map(payeeId => {
          const payee = groupMembers.value.find(m => String(m.id) === String(payeeId));
          return payee ? payee.name : `User ${payeeId}`;
        });
        payeeNames = payeesList.join(", ");
      } else if (expense.payee_id && expense.payee_id !== 'all') {
        // Legacy support for older expenses with single payee_id
        const payee = groupMembers.value.find(m => String(m.id) === String(expense.payee_id));
        payeeNames = payee ? payee.name : `User ${expense.payee_id}`;
      }

      return {
        id: `${expense.user_id}-${expense.date}`,
        description: expense.description || "No description",
        amount: expense.amount,
        currency: expense.base_currency,
        convertedAmount: Number(convertedAmount).toFixed(2),
        displayCurrency: displayCurrency.value,
        category: expense.category || "Other",
        addedBy: payerName,
        payee: payeeNames,
        date: expense.date,
        location: expense.location,
        is_paid: expense.is_paid
      };
    }));
  } catch (error) {
    console.error("Error fetching expenses:", error);
  }
};

const fetchGroupMembers = async () => {
  try {
    // Get readiness status from expense-management service instead of finance service
    const readinessResponse = await fetch(`http://localhost:5007/api/expenses/readiness/${route.params.tripId}`);
    
    if (readinessResponse.ok) {
      const data = await readinessResponse.json();
      groupMembers.value = data.users.map(user => ({
        id: user.user_id,
        name: user.name || `User ${user.user_id}`,
        ready: user.ready
      }));
      
      // Check if trip is ready for settlement
      if (data.all_ready) {
        await calculateSettlement();
      }
    } else {
      console.error("Failed to fetch readiness status:", readinessResponse.statusText);
    }
  } catch (error) {
    console.error("Error fetching group members:", error);
  }
};

const addExpense = async () => {
  try {
    // Check if user_id is set, if not use the current user's ID
    if (!newExpense.value.user_id) {
      newExpense.value.user_id = currentUserId.value;
    }

    // Format the expense data for the expense management service
    const expenseData = {
      trip_id: String(route.params.tripId), // Convert to string to match DB column type
      user_id: String(newExpense.value.user_id), // Use selected payer or current user
      date: new Date().toISOString().split("T")[0], // Current date in YYYY-MM-DD format
      location: trip.value.city || "Unknown",
      amount: parseFloat(newExpense.value.amount),
      base_currency: newExpense.value.currency || "SGD",
      description: newExpense.value.description,
      is_paid: false,
      category: newExpense.value.category,
      payees: newExpense.value.payees.includes("all") ? ["all"] : newExpense.value.payees.map(id => String(id))
    };

    console.log('Sending expense data:', expenseData);
    // Use the expense-management service instead of finance service directly
    const response = await fetch('http://localhost:5007/api/expenses', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(expenseData)
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(`HTTP error! Status: ${response.status} Error: ${errorData.error}`);
    }
    
    newExpense.value = {
      amount: "",
      currency: trip.value.localCurrency,
      description: "",
      category: "",
      user_id: currentUserId.value,
      payees: ["all"],
    };
    await fetchExpenses();
  } catch (error) {
    console.error("Error adding expense:", error);
  }
};

const markAsReady = async () => {
  try {
    // Get user details from stored user object
    let userName = `User ${currentUserId.value}`;
    let userEmail = `${currentUserId.value}@example.com`;
    
    const storedUser = localStorage.getItem('user');
    if (storedUser) {
      try {
        const userObj = JSON.parse(storedUser);
        userName = userObj.first_name && userObj.last_name ? 
          `${userObj.first_name} ${userObj.last_name}`.trim() : 
          userObj.name || userName;
        userEmail = userObj.email || userEmail;
      } catch (e) {
        console.error("Error parsing user from localStorage", e);
      }
    }
    
    // Fallback to direct localStorage items if available
    userName = localStorage.getItem('userName') || userName;
    userEmail = localStorage.getItem('userEmail') || userEmail;
    
    // Ensure user ID is sent as a string to match DB column type
    const userId = String(currentUserId.value);
    
    // Use expense-management service instead of directly calling finance service
    const response = await fetch(`http://localhost:5007/api/expenses/readiness/${route.params.tripId}/${userId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        name: userName,
        email: userEmail
      })
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }
    
    const data = await response.json();
    
    // Update the current user's ready status locally
    const updatedMembers = groupMembers.value.map(member => {
      // Compare as strings to ensure type consistency
      if (String(member.id) === String(userId)) {
        return { ...member, ready: true };
      }
      return member;
    });
    groupMembers.value = updatedMembers;
    
    // If all members are ready, the backend should have triggered settlement calculation
    if (data.all_ready) {
      await calculateSettlement();
      showSettlementModal.value = true;
    }
  } catch (error) {
    console.error("Error marking as ready:", error);
  }
};

const calculateSettlement = async () => {
  try {
    // First log what we're doing
    console.log(`Calculating settlement for trip ${route.params.tripId}...`);
    
    // Use expense-management service instead of finance service directly
    const response = await fetch(`http://localhost:5007/api/expenses/calculate/${route.params.tripId}`);
    if (!response.ok) {
      const errorText = await response.text();
      console.error(`Settlement calculation error (${response.status}):`, errorText);
      throw new Error(`HTTP error! Status: ${response.status}`);
    }
    
    const data = await response.json();
    console.log('Settlement data received:', data);
    
    // Store the settlements data
    settlementDetails.value = data.settlements || [];
    
    // Store currency
    settlementCurrency.value = data.currency || 'SGD';
    
  } catch (error) {
    console.error("Error calculating settlement:", error);
  }
};

const viewSettlementDetails = () => {
  showSettlementModal.value = true;
};

const formatDate = (date) => {
  return new Date(date).toLocaleDateString();
};

const updateDisplayCurrency = async () => {
  try {
    // Update exchange rate for the new display currency
    const rateResponse = await fetch(
      `http://localhost:5007/api/expenses/convert/${trip.value.localCurrency}/${displayCurrency.value}/1.0`,
      {
        method: 'GET',
        headers: {
          'Accept': 'application/json'
        }
      }
    );
    
    if (rateResponse.ok) {
      const rateData = await rateResponse.json();
      if (rateData && typeof rateData === 'object') {
        if ('rate' in rateData) {
          trip.value.exchangeRate = Number(rateData.rate).toFixed(4);
        } else if ('converted_amount' in rateData) {
          trip.value.exchangeRate = Number(rateData.converted_amount).toFixed(4);
        }
      }
    }
    
    // Refresh expenses to update converted amounts
    await fetchExpenses();
  } catch (error) {
    console.error('Error updating display currency:', error);
  }
};

onMounted(() => {
  // Get user ID from stored user object
  const storedUser = localStorage.getItem('user');
  if (storedUser) {
    try {
      const userObj = JSON.parse(storedUser);
      // Store ID as string to match database column type
      currentUserId.value = userObj.id ? String(userObj.id) : null;
    } catch (e) {
      console.error("Error parsing user from localStorage", e);
      // Fallback to direct userId if available
      const userId = localStorage.getItem('userId');
      currentUserId.value = userId ? String(userId) : null;
    }
  } else {
    // Fallback to direct userId if available
    const userId = localStorage.getItem('userId');
    currentUserId.value = userId ? String(userId) : null;
  }
  
  if (!currentUserId.value) {
    // Default user ID for development - should be removed in production
    currentUserId.value = "1";
    console.warn("Using default user ID: 1");
  }
  
  // Initialize newExpense with the current user ID
  newExpense.value.user_id = currentUserId.value;
  
  fetchTripDetails();
  fetchGroupMembers();
});
</script> 