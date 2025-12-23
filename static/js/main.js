// Main JavaScript File

document.addEventListener('DOMContentLoaded', function() {
  console.log('Static files loaded successfully!');
  
  // Add your scripts here
});

// Utility functions
const Utils = {
  // Add your utility functions here
  formatDate: function(date) {
    return new Date(date).toLocaleDateString();
  },
  
  formatCurrency: function(amount) {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount);
  }
};
