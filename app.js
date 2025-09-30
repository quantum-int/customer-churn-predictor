// Customer Churn Prediction Dashboard Application
class ChurnDashboard {
    constructor() {
        this.currentView = 'dashboard';
        this.customers = [];
        this.selectedCustomers = new Set();
        this.currentPage = 1;
        this.itemsPerPage = 10;
        this.charts = {};
        
        this.init();
    }

    init() {
        // Ensure loading overlay is hidden on initialization
        this.showLoading(false);
        
        this.generateSyntheticData();
        this.setupEventListeners();
        this.setupCharts();
        this.updateDateTime();
        this.populateHighRiskTable();
        this.populateCustomerTable();
        
        // Update date/time every minute
        setInterval(() => this.updateDateTime(), 60000);

        // Failsafe: ensure overlay is hidden after full page load
        window.addEventListener('load', () => this.showLoading(false));
    }

    generateSyntheticData() {
        const firstNames = ['John', 'Sarah', 'Mike', 'Emma', 'Robert', 'Lisa', 'David', 'Jennifer', 'Michael', 'Ashley',
            'James', 'Jessica', 'William', 'Amanda', 'Richard', 'Melissa', 'Joseph', 'Deborah', 'Thomas', 'Stephanie'];
        const lastNames = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 'Rodriguez', 'Martinez',
            'Hernandez', 'Lopez', 'Gonzalez', 'Wilson', 'Anderson', 'Thomas', 'Taylor', 'Moore', 'Jackson', 'Martin'];
        const locations = ['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix', 'Philadelphia', 'San Antonio', 'San Diego'];
        const contracts = ['Monthly', 'One Year', 'Two Year'];
        
        // Generate 200 synthetic customers
        for (let i = 1; i <= 200; i++) {
            const firstName = firstNames[Math.floor(Math.random() * firstNames.length)];
            const lastName = lastNames[Math.floor(Math.random() * lastNames.length)];
            const age = Math.floor(Math.random() * 50) + 18;
            const monthlyBill = parseFloat((Math.random() * 200 + 30).toFixed(2));
            const satisfactionScore = parseFloat((Math.random() * 10 + 1).toFixed(1));
            const subscriptionLength = Math.floor(Math.random() * 36) + 1;
            const serviceCalls = Math.floor(Math.random() * 10);
            const daysSinceActivity = Math.floor(Math.random() * 30);
            
            // Calculate risk based on realistic factors
            let riskScore = 0;
            if (age < 25 || age > 60) riskScore += 15;
            if (monthlyBill > 150) riskScore += 10;
            if (satisfactionScore < 5) riskScore += 20;
            if (subscriptionLength < 6) riskScore += 15;
            if (serviceCalls > 5) riskScore += 15;
            if (daysSinceActivity > 7) riskScore += 20;
            
            riskScore += Math.random() * 20; // Add some randomness
            riskScore = Math.min(95, Math.max(5, riskScore)); // Cap between 5-95%
            
            let riskLevel = 'Low Risk';
            if (riskScore > 70) riskLevel = 'High Risk';
            else if (riskScore > 40) riskLevel = 'Medium Risk';
            
            const customer = {
                customer_id: `CUST_${String(i).padStart(6, '0')}`,
                first_name: firstName,
                last_name: lastName,
                name: `${firstName} ${lastName}`,
                age,
                gender: Math.random() > 0.5 ? 'Male' : 'Female',
                location: locations[Math.floor(Math.random() * locations.length)],
                monthly_bill: monthlyBill,
                contract_type: contracts[Math.floor(Math.random() * contracts.length)],
                satisfaction_score: satisfactionScore,
                subscription_length: subscriptionLength,
                service_calls: serviceCalls,
                days_since_activity: daysSinceActivity,
                credit_score: Math.floor(Math.random() * 400) + 450,
                risk_score: parseFloat(riskScore.toFixed(1)),
                risk_level: riskLevel,
                last_activity: this.getRelativeTime(daysSinceActivity),
                services: {
                    phone: Math.random() > 0.3,
                    internet: Math.random() > 0.2,
                    streaming: Math.random() > 0.6,
                    security: Math.random() > 0.7
                }
            };
            
            this.customers.push(customer);
        }
        
        // Sort by risk score descending
        this.customers.sort((a, b) => b.risk_score - a.risk_score);
    }

    getRelativeTime(days) {
        if (days === 0) return 'Today';
        if (days === 1) return '1 day ago';
        if (days < 7) return `${days} days ago`;
        const weeks = Math.floor(days / 7);
        if (weeks === 1) return '1 week ago';
        return `${weeks} weeks ago`;
    }

    setupEventListeners() {
        // Navigation
        document.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const view = e.target.closest('.nav-link').dataset.view;
                this.switchView(view);
            });
        });

        // Prediction form
        const predictionForm = document.getElementById('predictionForm');
        if (predictionForm) {
            predictionForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.handlePrediction(e.target);
            });
        }

        // Customer search and filter
        const customerSearch = document.getElementById('customerSearch');
        if (customerSearch) {
            customerSearch.addEventListener('input', (e) => {
                this.filterCustomers();
            });
        }

        const riskFilter = document.getElementById('riskFilter');
        if (riskFilter) {
            riskFilter.addEventListener('change', () => {
                this.filterCustomers();
            });
        }

        // Pagination
        const prevPageBtn = document.getElementById('prevPage');
        if (prevPageBtn) {
            prevPageBtn.addEventListener('click', () => this.previousPage());
        }
        
        const nextPageBtn = document.getElementById('nextPage');
        if (nextPageBtn) {
            nextPageBtn.addEventListener('click', () => this.nextPage());
        }

        // Select all checkbox
        const selectAllBtn = document.getElementById('selectAll');
        if (selectAllBtn) {
            selectAllBtn.addEventListener('change', (e) => {
                this.toggleSelectAll(e.target.checked);
            });
        }

        // Export button
        document.querySelectorAll('button').forEach(btn => {
            if (btn.textContent.includes('Export Report')) {
                btn.addEventListener('click', () => this.generateReport());
            }
        });
    }

    setupCharts() {
        // Risk Distribution Chart
        const riskCtx = document.getElementById('riskChart');
        if (riskCtx) {
            this.charts.risk = new Chart(riskCtx, {
                type: 'doughnut',
                data: {
                    labels: ['Low Risk', 'Medium Risk', 'High Risk'],
                    datasets: [{
                        data: [1199, 567, 234],
                        backgroundColor: ['#1FB8CD', '#FFC185', '#B4413C'],
                        borderWidth: 2,
                        borderColor: '#ffffff'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'bottom',
                            labels: {
                                padding: 20,
                                usePointStyle: true
                            }
                        }
                    }
                }
            });
        }

        // Monthly Trends Chart
        const trendCtx = document.getElementById('trendChart');
        if (trendCtx) {
            this.charts.trend = new Chart(trendCtx, {
                type: 'line',
                data: {
                    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                    datasets: [{
                        label: 'Churn Rate (%)',
                        data: [22.1, 23.5, 21.8, 25.2, 24.7, 24.3],
                        borderColor: '#1FB8CD',
                        backgroundColor: 'rgba(31, 184, 205, 0.1)',
                        borderWidth: 3,
                        fill: true,
                        tension: 0.4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: false
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            max: 30,
                            ticks: {
                                callback: function(value) {
                                    return value + '%';
                                }
                            }
                        }
                    }
                }
            });
        }
    }

    switchView(viewName) {
        // Update navigation
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.remove('active');
        });
        const activeLink = document.querySelector(`[data-view="${viewName}"]`);
        if (activeLink) {
            activeLink.classList.add('active');
        }

        // Update views
        document.querySelectorAll('.view').forEach(view => {
            view.classList.remove('active');
        });
        const activeView = document.getElementById(`${viewName}-view`);
        if (activeView) {
            activeView.classList.add('active');
        }

        this.currentView = viewName;

        // Trigger specific view logic
        if (viewName === 'customers') {
            this.populateCustomerTable();
        }
    }

    updateDateTime() {
        const now = new Date();
        const options = {
            weekday: 'long',
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        };
        const dateString = now.toLocaleDateString('en-US', options);
        const dateElement = document.getElementById('current-date');
        if (dateElement) {
            dateElement.textContent = dateString;
        }
    }

    populateHighRiskTable() {
        const tableBody = document.getElementById('highRiskTableBody');
        if (!tableBody) return;

        const highRiskCustomers = this.customers.filter(c => c.risk_level === 'High Risk').slice(0, 5);
        
        tableBody.innerHTML = highRiskCustomers.map(customer => `
            <tr>
                <td>${customer.customer_id}</td>
                <td>${customer.name}</td>
                <td>
                    <span class="risk-badge risk-badge--high">
                        ${customer.risk_score}% High Risk
                    </span>
                </td>
                <td>$${customer.monthly_bill.toFixed(2)}</td>
                <td>${customer.last_activity}</td>
                <td>
                    <button class="action-btn primary" onclick="app.viewCustomer('${customer.customer_id}')">
                        <i class="fas fa-eye"></i>
                    </button>
                    <button class="action-btn" onclick="app.contactCustomer('${customer.customer_id}')">
                        <i class="fas fa-phone"></i>
                    </button>
                    <button class="action-btn danger" onclick="app.flagCustomer('${customer.customer_id}')">
                        <i class="fas fa-flag"></i>
                    </button>
                </td>
            </tr>
        `).join('');
    }

    populateCustomerTable() {
        const tableBody = document.getElementById('customerTableBody');
        if (!tableBody) return;

        const filteredCustomers = this.getFilteredCustomers();
        const startIndex = (this.currentPage - 1) * this.itemsPerPage;
        const endIndex = startIndex + this.itemsPerPage;
        const pageCustomers = filteredCustomers.slice(startIndex, endIndex);

        tableBody.innerHTML = pageCustomers.map(customer => `
            <tr>
                <td>
                    <input type="checkbox" onchange="app.toggleCustomerSelection('${customer.customer_id}', this.checked)">
                </td>
                <td>${customer.customer_id}</td>
                <td>${customer.name}</td>
                <td>${customer.age}</td>
                <td>$${customer.monthly_bill.toFixed(2)}</td>
                <td>
                    <span class="risk-badge risk-badge--${customer.risk_level.toLowerCase().replace(' ', '')}">
                        ${customer.risk_level}
                    </span>
                </td>
                <td>${customer.satisfaction_score}/10</td>
                <td>${customer.last_activity}</td>
                <td>
                    <button class="action-btn primary" onclick="app.viewCustomer('${customer.customer_id}')">
                        <i class="fas fa-eye"></i>
                    </button>
                    <button class="action-btn" onclick="app.predictCustomer('${customer.customer_id}')">
                        <i class="fas fa-crystal-ball"></i>
                    </button>
                </td>
            </tr>
        `).join('');

        this.updatePagination(filteredCustomers.length);
        this.updateBulkActions();
    }

    getFilteredCustomers() {
        const searchTerm = document.getElementById('customerSearch')?.value.toLowerCase() || '';
        const riskFilter = document.getElementById('riskFilter')?.value || '';

        return this.customers.filter(customer => {
            const matchesSearch = customer.name.toLowerCase().includes(searchTerm) ||
                                customer.customer_id.toLowerCase().includes(searchTerm);
            const matchesRisk = !riskFilter || customer.risk_level === riskFilter + ' Risk';
            return matchesSearch && matchesRisk;
        });
    }

    filterCustomers() {
        this.currentPage = 1;
        this.populateCustomerTable();
    }

    updatePagination(totalItems) {
        const totalPages = Math.ceil(totalItems / this.itemsPerPage);
        const paginationInfo = document.querySelector('.pagination-info');
        const prevBtn = document.getElementById('prevPage');
        const nextBtn = document.getElementById('nextPage');

        if (paginationInfo) {
            paginationInfo.textContent = `Page ${this.currentPage} of ${totalPages}`;
        }

        if (prevBtn) {
            prevBtn.disabled = this.currentPage <= 1;
        }

        if (nextBtn) {
            nextBtn.disabled = this.currentPage >= totalPages;
        }
    }

    previousPage() {
        if (this.currentPage > 1) {
            this.currentPage--;
            this.populateCustomerTable();
        }
    }

    nextPage() {
        const filteredCustomers = this.getFilteredCustomers();
        const totalPages = Math.ceil(filteredCustomers.length / this.itemsPerPage);
        if (this.currentPage < totalPages) {
            this.currentPage++;
            this.populateCustomerTable();
        }
    }

    toggleSelectAll(checked) {
        const checkboxes = document.querySelectorAll('#customerTableBody input[type="checkbox"]');
        checkboxes.forEach(checkbox => {
            checkbox.checked = checked;
            const customerId = checkbox.closest('tr').cells[1].textContent;
            if (checked) {
                this.selectedCustomers.add(customerId);
            } else {
                this.selectedCustomers.delete(customerId);
            }
        });
        this.updateBulkActions();
    }

    toggleCustomerSelection(customerId, selected) {
        if (selected) {
            this.selectedCustomers.add(customerId);
        } else {
            this.selectedCustomers.delete(customerId);
        }
        this.updateBulkActions();
    }

    updateBulkActions() {
        const bulkBtn = document.getElementById('bulkActionBtn');
        if (bulkBtn) {
            const count = this.selectedCustomers.size;
            bulkBtn.textContent = `Bulk Actions (${count} selected)`;
            bulkBtn.disabled = count === 0;
        }
    }

    handlePrediction(form) {
        this.showLoading(true);

        // Simulate API call delay
        setTimeout(() => {
            const formData = new FormData(form);
            const prediction = this.calculateChurnProbability(formData);
            this.displayPredictionResults(prediction);
            this.showLoading(false);
        }, 400);
    }

    calculateChurnProbability(formData) {
        const age = parseInt(formData.get('age'));
        const monthlyBill = parseFloat(formData.get('monthlyBill'));
        const contractType = formData.get('contractType');
        const subscriptionLength = parseInt(formData.get('subscriptionLength'));
        const satisfaction = parseInt(formData.get('satisfaction'));
        const serviceCalls = parseInt(formData.get('serviceCalls'));
        const daysSinceActivity = parseInt(formData.get('daysSinceActivity'));
        const creditScore = parseInt(formData.get('creditScore'));
        
        // Simple churn prediction algorithm
        let riskScore = 0;
        
        // Age factor
        if (age < 25 || age > 60) riskScore += 15;
        else if (age >= 35 && age <= 50) riskScore -= 5;
        
        // Bill factor
        if (monthlyBill > 150) riskScore += 12;
        else if (monthlyBill < 50) riskScore += 8;
        
        // Contract factor
        if (contractType === 'Monthly') riskScore += 20;
        else if (contractType === 'Two Year') riskScore -= 15;
        
        // Loyalty factor
        if (subscriptionLength < 6) riskScore += 18;
        else if (subscriptionLength > 24) riskScore -= 10;
        
        // Satisfaction factor
        if (satisfaction <= 3) riskScore += 25;
        else if (satisfaction >= 8) riskScore -= 15;
        
        // Service issues
        if (serviceCalls > 5) riskScore += 15;
        else if (serviceCalls === 0) riskScore -= 5;
        
        // Engagement
        if (daysSinceActivity > 14) riskScore += 20;
        else if (daysSinceActivity <= 1) riskScore -= 10;
        
        // Credit score
        if (creditScore < 600) riskScore += 10;
        else if (creditScore > 750) riskScore -= 5;
        
        // Add some randomness
        riskScore += (Math.random() - 0.5) * 10;
        
        // Normalize to 0-100%
        riskScore = Math.max(5, Math.min(95, riskScore + 30));
        
        const probability = parseFloat(riskScore.toFixed(1));
        let riskLevel = 'Low';
        let recommendations = [];
        
        if (probability > 70) {
            riskLevel = 'High';
            recommendations = [
                'Immediate retention call recommended',
                'Offer loyalty discount or upgrade incentive',
                'Schedule customer success manager meeting',
                'Review and address service quality issues'
            ];
        } else if (probability > 40) {
            riskLevel = 'Medium';
            recommendations = [
                'Monitor customer engagement closely',
                'Send satisfaction survey',
                'Offer service optimization consultation',
                'Provide proactive customer support'
            ];
        } else {
            riskLevel = 'Low';
            recommendations = [
                'Continue excellent service delivery',
                'Consider upselling opportunities',
                'Include in referral program',
                'Send appreciation communication'
            ];
        }
        
        return { probability, riskLevel, recommendations };
    }

    displayPredictionResults(prediction) {
        const outputDiv = document.getElementById('predictionOutput');
        if (!outputDiv) return;

        const riskClass = prediction.riskLevel.toLowerCase() + '-risk';
        
        outputDiv.innerHTML = `
            <div class="prediction-output">
                <div class="churn-probability ${riskClass}">
                    ${prediction.probability}%
                </div>
                <div class="risk-gauge">
                    <div class="gauge-value">${prediction.probability}%</div>
                </div>
                <h4>Risk Level: <span class="${riskClass}">${prediction.riskLevel}</span></h4>
                
                <div class="recommendations">
                    <h4>Recommended Actions:</h4>
                    <ul>
                        ${prediction.recommendations.map(rec => `
                            <li>
                                <i class="fas fa-lightbulb"></i>
                                <span>${rec}</span>
                            </li>
                        `).join('')}
                    </ul>
                </div>
                
                <div class="prediction-actions" style="margin-top: 20px; display: flex; gap: 12px;">
                    <button class="btn btn--primary" onclick="app.saveCustomerPrediction()">
                        <i class="fas fa-save"></i>
                        Save Customer
                    </button>
                    <button class="btn btn--secondary" onclick="app.generateReport()">
                        <i class="fas fa-file-pdf"></i>
                        Generate Report
                    </button>
                </div>
            </div>
        `;
    }

    showLoading(show) {
        const overlay = document.getElementById('loadingOverlay');
        if (overlay) {
            if (show) {
                overlay.classList.remove('hidden');
            } else {
                overlay.classList.add('hidden');
            }
        }
    }

    showNotification(message, type = 'success') {
        const container = document.getElementById('notifications');
        if (!container) return;

        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.innerHTML = `
            <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
            <span>${message}</span>
        `;

        container.appendChild(notification);

        // Auto remove after 3 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 3000);
    }

    // Action methods
    viewCustomer(customerId) {
        const customer = this.customers.find(c => c.customer_id === customerId);
        if (customer) {
            this.showNotification(`Viewing details for ${customer.name}`, 'success');
            // In a real app, this would open a detailed customer view
        }
    }

    contactCustomer(customerId) {
        const customer = this.customers.find(c => c.customer_id === customerId);
        if (customer) {
            this.showNotification(`Initiating contact with ${customer.name}`, 'success');
        }
    }

    flagCustomer(customerId) {
        const customer = this.customers.find(c => c.customer_id === customerId);
        if (customer) {
            this.showNotification(`${customer.name} has been flagged for review`, 'warning');
        }
    }

    predictCustomer(customerId) {
        const customer = this.customers.find(c => c.customer_id === customerId);
        if (customer) {
            // Switch to prediction view and prefill form
            this.switchView('predict');
            setTimeout(() => {
                this.prefillPredictionForm(customer);
            }, 100);
        }
    }

    prefillPredictionForm(customer) {
        const form = document.getElementById('predictionForm');
        if (!form) return;

        // Prefill form fields
        const ageField = form.querySelector('[name="age"]');
        if (ageField) ageField.value = customer.age;
        
        const genderField = form.querySelector('[name="gender"]');
        if (genderField) genderField.value = customer.gender;
        
        const billField = form.querySelector('[name="monthlyBill"]');
        if (billField) billField.value = customer.monthly_bill;
        
        const contractField = form.querySelector('[name="contractType"]');
        if (contractField) contractField.value = customer.contract_type;
        
        const lengthField = form.querySelector('[name="subscriptionLength"]');
        if (lengthField) lengthField.value = customer.subscription_length;
        
        const satisfactionField = form.querySelector('[name="satisfaction"]');
        if (satisfactionField) {
            satisfactionField.value = Math.round(customer.satisfaction_score);
            const satisfactionValue = document.getElementById('satisfactionValue');
            if (satisfactionValue) satisfactionValue.textContent = Math.round(customer.satisfaction_score);
        }
        
        const callsField = form.querySelector('[name="serviceCalls"]');
        if (callsField) callsField.value = customer.service_calls;
        
        const activityField = form.querySelector('[name="daysSinceActivity"]');
        if (activityField) activityField.value = customer.days_since_activity;
        
        const creditField = form.querySelector('[name="creditScore"]');
        if (creditField) creditField.value = customer.credit_score;

        // Set services
        form.querySelectorAll('input[name="services"]').forEach(checkbox => {
            checkbox.checked = customer.services[checkbox.value] || false;
        });

        this.showNotification(`Form prefilled with ${customer.name}'s data`, 'success');
    }

    saveCustomerPrediction() {
        this.showNotification('Customer prediction saved successfully!', 'success');
    }

    generateReport() {
        this.showLoading(true);
        setTimeout(() => {
            this.showLoading(false);
            this.showNotification('Report generated and ready for download', 'success');
        }, 800);
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.app = new ChurnDashboard();
});