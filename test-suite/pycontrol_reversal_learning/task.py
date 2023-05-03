from poke import Poke
from timer import Timer
from event_handler import EventHandler
from shelley.shelleypy import operation, system, claim

# -------------------------------------------------------------------------
# Variables.
# -------------------------------------------------------------------------

# Parameters.
v.session_duration = 1 * hour  # Session duration.
v.reward_durations = [100, 100]  # Reward delivery duration (ms) [left, right].
v.ITI_duration = 1 * second  # Inter trial interval duration.
v.threshold = 0.75  # Performance treshold used for triggering reversal.
v.tau = 8  # Time constant for moving average of choices (trials).
v.trials_post_threshold = [5, 15]  # Trials after threshold crossing before reversal occurs [min, max].
v.good_prob = 0.8  # Reward probabilities on the good side.
v.bad_prob = 0.2  # Reward probabilities on the bad side.

# Variables.
v.n_rewards = 0  # Number of rewards obtained.
v.n_trials = 0  # Number of trials recieved.
v.n_blocks = 0  # Number of reversals.
v.good_side = choice(['left', 'right'])  # Which side is currently good.
v.correct_mov_ave = exp_mov_ave(tau=v.tau, init_value=0.5)  # Moving average of correct/incorrect choices
v.threshold_crossed = False  # Whether performance threshold has been crossed.
v.trials_till_reversal = 0  # Used after threshold crossing to trigger reversal.


# -------------------------------------------------------------------------
# Non-state machine code.
# -------------------------------------------------------------------------

def get_trial_outcome(chosen_side):
    # Function called after choice is made which determines trial outcome,
    # controls when reversals happen, and prints trial information.

    # Determine trial outcome.
    if chosen_side == v.good_side:  # Subject choose good side.
        v.outcome = withprob(v.good_prob)
        v.correct_mov_ave.update(1)

    else:
        v.outcome = withprob(v.bad_prob)
        v.correct_mov_ave.update(0)

    # Determine when reversal occurs.
    if v.threshold_crossed:  # Subject has already crossed threshold.
        v.trials_till_reversal -= 1
        if v.trials_till_reversal == 0:  # Trigger reversal.
            v.good_side = 'left' if (v.good_side == 'right') else 'right'
            v.correct_mov_ave.value = 1 - v.correct_mov_ave.value
            v.threshold_crossed = False
            v.n_blocks += 1
    else:  # Check for threshold crossing.
        if v.correct_mov_ave.value > v.threshold:
            v.threshold_crossed = True
            v.trials_till_reversal = randint(*v.trials_post_threshold)

    # Print trial information.
    v.n_trials += 1
    v.n_rewards += v.outcome
    v.choice = chosen_side
    v.ave_correct = v.correct_mov_ave.value
    print_variables(['n_trials', 'n_rewards', 'n_blocks', 'good_side', 'choice', 'outcome', 'ave_correct'])
    return v.outcome


# -------------------------------------------------------------------------
# State machine code.
# -------------------------------------------------------------------------

# Run start and stop behaviour.

def run_start():
    # Set session timer and turn on houslight.
    set_timer('session_timer', v.session_duration)
    hw.houselight.on()


def run_end():
    # Turn off all hardware outputs.
    hw.off()


# State behaviour logic

@system(uses={"center_poke": "Poke", "left_poke": "Poke", "right_poke": "Poke", "event_handler": "EventHandler", "timer": "Timer"})
class Task:

    def __init__(self, hw_bind):
        self.timer = Timer()
        self.center_poke = Poke(hw_bind.center_poke)
        self.left_poke = Poke(hw_bind.left_poke)
        self.right_poke = Poke(hw_bind.right_poke)
        self.event_handler = EventHandler()

    @op_initial
    def init_trial(self):
        self.center_poke.led_on()
        match self.event_handler.next():  # wait for next event
            case 'center_poke':
                self.event_handler.center_poke()
                self.center_poke.led_off()
                return "choice_state"
            case 'session_timer':
                self.event_handler.session_timer()
                self.center_poke.led_off()
                return "stop_trial"
            # TODO: case _: error!

    @op
    def choice_state(self):
        """
        Wait for left or right choice, evaluate if reward is delivered using get_trial_outcome function.
        """
        self.left_poke.led_on()
        self.right_poke.led_on()

        match self.event_handler.next():  # wait for next event
            case 'left_poke':
                self.event_handler.left_poke()
                if get_trial_outcome('left'):
                    self.left_poke.led_off()
                    self.right_poke.led_off()
                    return "left_reward"
            case 'right_poke':
                self.event_handler.right_poke()
                if get_trial_outcome('right'):
                    self.left_poke.led_off()
                    self.right_poke.led_off()
                    return "right_reward"
            # TODO: case _: error!

        # getting here means trial outcome failed
        self.left_poke.led_off()
        self.right_poke.led_off()
        return "inter_trial_interval"

    @op
    def left_reward(self):
        """
        Deliver reward to left poke.
        """
        self.left_poke.sol_on()
        self.timer.wait(v.reward_durations[0])
        self.left_poke.sol_off()
        return "inter_trial_interval"

    @op
    def right_reward(self):
        """
        Deliver reward to right poke.
        """
        self.right_poke.sol_on()
        self.timer.wait(v.reward_durations[1])
        self.right_poke.sol_off()
        return "inter_trial_interval"

    @op
    def inter_trial_interval(self):
        """
        Go to init trial after specified delay.
        """
        self.timer.wait(v.ITI_duration)
        return "init_trial"

    # State independent behaviour.
    @op_final
    def stop_trial(self):
        stop_framework()
        return ""

    #
    # @operation(next=["init_trial", "init_trial_exit", "choice_state"])
    # def init_trial(self, event):
    #     if event == 'entry':
    #         self.center_poke.led_on()
    #         return "init_trial"
    #     elif event == 'exit':
    #         return "init_trial_exit"
    #     elif event == 'center_poke':
    #         self.center_poke.led_off()
    #         return "choice_state"
    #     elif event == 'session_timer':
    #         return "stop"
    #     return "init_trial"

    # @operation(next=["choice_state", "left_reward", "inter_trial_interval", "right_reward"])
    # def choice_state(self, event):
    #     # Wait for left or right choice, evaluate if reward is delivered using get_trial_outcome function.
    #     if event == 'entry':
    #         self.left_poke.led_on()
    #         self.right_poke.led_on()
    #     elif event == 'exit':
    #         self.left_poke.led_off()
    #         self.right_poke_poke.led_off()
    #     elif event == 'left_poke':
    #         if get_trial_outcome('left'):
    #             return "left_reward"
    #         else:
    #             return "inter_trial_interval"
    #     elif event == 'right_poke':
    #         if get_trial_outcome('right'):
    #             return "right_reward"
    #         else:
    #             return "inter_trial_interval"
    #
    #     return "choice_state"
