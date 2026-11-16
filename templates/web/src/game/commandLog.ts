// Records every command the sim receives, with its tick, so a bug report can replay the run
// (PLAYTEST-AND-BUGS.md, sections 5 and 6). Ticks are stored relative to the start of the log.

import { serialize, type Command, type Config, type World } from "../sim";

export interface LoggedCommand {
  tick: number;
  type: string;
  [key: string]: unknown;
}

export class CommandLog {
  private startTick = 0;
  private startSave: string | null = null;
  readonly commands: LoggedCommand[] = [];

  constructor(
    readonly seed: number,
    readonly config: Config,
  ) {}

  record(world: World, commands: readonly Command[]): void {
    for (const c of commands) this.commands.push({ tick: world.tick - this.startTick, ...c });
  }

  /** Call after loading a save, or when the log grows too large: the log restarts from this world. */
  rebase(world: World): void {
    this.startTick = world.tick;
    this.startSave = serialize(world);
    this.commands.length = 0;
  }

  toReplay(world: World) {
    return {
      format: 1,
      seed: this.seed,
      config: this.config,
      start_save: this.startSave,
      ticks: world.tick - this.startTick,
      commands: [...this.commands],
    };
  }
}
