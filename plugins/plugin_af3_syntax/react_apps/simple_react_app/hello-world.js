/**
 * Simple React App - Hello World Component
 * 
 * This is a React component written in vanilla JavaScript (no JSX).
 * It demonstrates the basic syntax for React apps in Airflow 3.
 */

console.log('🌟 Simple React App component loading...');

// ============================================================================
// 🎯 Simple Hello World React Component
// ============================================================================
function SimpleHelloWorld(props) {
    console.log('SimpleHelloWorld rendered with props:', props);
    
    // 🎣 React hooks for state management
    const [count, setCount] = React.useState(0);
    const [message, setMessage] = React.useState('Hello from React! 🌟');
    
    // 🎯 Event handlers
    const handleButtonClick = () => {
        setCount(count + 1);
        setMessage(`Button clicked ${count + 1} times! 🎉`);
        console.log('Button clicked, count:', count + 1);
    };
    
    const handleReset = () => {
        setCount(0);
        setMessage('Hello from React! 🌟');
        console.log('Reset clicked');
    };
    
    // 🎨 Inline styles (full page layout)
    const containerStyle = {
        background: 'linear-gradient(135deg, #AF76FF 0%, #0AA6FF 100%)',
        color: 'white',
        padding: '40px',
        borderRadius: '16px',
        margin: '40px auto',
        textAlign: 'center',
        fontFamily: 'system-ui, -apple-system, sans-serif',
        boxShadow: '0 8px 32px rgba(175, 118, 255, 0.3)',
        maxWidth: '600px',
        minHeight: '400px',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center'
    };
    
    const buttonStyle = {
        background: 'rgba(255, 255, 255, 0.2)',
        color: 'white',
        border: '1px solid rgba(255, 255, 255, 0.3)',
        borderRadius: '8px',
        padding: '10px 20px',
        margin: '5px',
        cursor: 'pointer',
        fontSize: '14px',
        fontWeight: '600',
        transition: 'all 0.2s ease'
    };
    
    const titleStyle = {
        fontSize: '28px',
        fontWeight: 'bold',
        marginBottom: '24px'
    };
    
    const messageStyle = {
        fontSize: '16px',
        marginBottom: '16px',
        minHeight: '24px'
    };
    
    const countStyle = {
        fontSize: '18px',
        fontWeight: 'bold',
        margin: '12px 0'
    };
    
    // 🏗️ Component render (using React.createElement)
    return React.createElement('div', { style: containerStyle }, [
        // Title
        React.createElement('div', { 
            key: 'title',
            style: titleStyle 
        }, '🌟 Simple React Component'),
        
        // Message
        React.createElement('div', { 
            key: 'message',
            style: messageStyle 
        }, message),
        
        // Count display
        React.createElement('div', { 
            key: 'count',
            style: countStyle 
        }, `Count: ${count}`),
        
        // Buttons container
        React.createElement('div', { key: 'buttons' }, [
            // Click button
            React.createElement('button', {
                key: 'click-btn',
                style: buttonStyle,
                onClick: handleButtonClick,
                onMouseEnter: (e) => {
                    e.target.style.background = 'rgba(255, 255, 255, 0.3)';
                    e.target.style.transform = 'translateY(-2px)';
                },
                onMouseLeave: (e) => {
                    e.target.style.background = 'rgba(255, 255, 255, 0.2)';
                    e.target.style.transform = 'translateY(0)';
                }
            }, '🎯 Click Me!'),
            
            // Reset button
            React.createElement('button', {
                key: 'reset-btn',
                style: buttonStyle,
                onClick: handleReset,
                onMouseEnter: (e) => {
                    e.target.style.background = 'rgba(255, 255, 255, 0.3)';
                    e.target.style.transform = 'translateY(-2px)';
                },
                onMouseLeave: (e) => {
                    e.target.style.background = 'rgba(255, 255, 255, 0.2)';
                    e.target.style.transform = 'translateY(0)';
                }
            }, '🔄 Reset')
        ]),
        
        // Info text
        React.createElement('div', { 
            key: 'info',
            style: { 
                fontSize: '12px', 
                marginTop: '16px', 
                opacity: 0.9 
            } 
        }, '💡 This is a React component on its own page!')
    ]);
}


// ============================================================================
// 🔧 Global Registration (CRITICAL!)
// ============================================================================

// This is the magic line that makes it work!
// The variable name MUST match the "name" in react_apps configuration
globalThis['React Example Plugin'] = SimpleHelloWorld;

// Also set the fallback that Airflow looks for
globalThis.AirflowPlugin = SimpleHelloWorld;

console.log('🌟 React component registered successfully:', {
    'React Example Plugin': typeof globalThis['React Example Plugin'],
    'AirflowPlugin': typeof globalThis.AirflowPlugin
});


// ============================================================================
// 📝 Development Notes
// ============================================================================
/*
🎯 Key Points:

1. **No JSX**: Use React.createElement instead of <div>
2. **Global Variable**: Must set globalThis['Simple Hello World'] = Component
3. **Props**: Airflow passes props like { dagId, runId, taskId } depending on location
4. **Hooks**: Can use useState, useEffect, etc. normally
5. **Styling**: Inline styles or external CSS (via FastAPI app)

🌍 Destinations Available:
- "nav" - Navigation menu (creates dedicated page)
- "dashboard" - Embedded in main dashboard  
- "dag" - Individual DAG pages
- "dag_run" - DAG run pages  
- "task" - Task pages
- "task_instance" - Task instance pages

🚀 Advanced Features:
- Access to Airflow context via props
- Can make API calls to Airflow REST API
- Full React ecosystem (hooks, context, etc.)
- Professional UI integration (not iframes)
*/
