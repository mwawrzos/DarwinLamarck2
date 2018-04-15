from experiment import Experiment
import toolboxes as t

def main():
    toolbox = t.environment(t.darwinian(t.sheep(count=100)), t.lamarckian(t.wolves(count=30)))
    experiment = Experiment(toolbox)
    experiment.run()

if __name__ == '__main__':
    main()