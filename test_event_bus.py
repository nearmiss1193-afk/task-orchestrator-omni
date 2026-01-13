from modules.self_healer import SelfHealingAgent

agent = SelfHealingAgent()

try:
    raise ValueError('demo error for self-healing')
except Exception as e:
    agent.log_error('demo_test', e, {'detail': 'testing event bus'})
